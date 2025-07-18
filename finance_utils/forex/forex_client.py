"""
Forex Data Client

This module handles all forex data fetching from Alpha Vantage API.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
import json
import logging

logger = logging.getLogger(__name__)

class ForexClient:
    """
    Client for fetching forex data from Alpha Vantage API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://www.alphavantage.co/query"):
        """
        Initialize the forex client
        
        Args:
            api_key: Alpha Vantage API key
            base_url: Base URL for Alpha Vantage API
        """
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        self.last_request_time = 0
        self.request_count = 0
        self.rate_limit_delay = 12  # seconds between requests (500 requests per day)
        
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """
        Make a rate-limited request to Alpha Vantage API
        
        Args:
            params: Request parameters
            
        Returns:
            JSON response data or None if failed
        """
        # Rate limiting
        time_since_last = time.time() - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        params['apikey'] = self.api_key
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            self.last_request_time = time.time()
            self.request_count += 1
            
            data = response.json()
            
            # Check for API errors
            if 'Error Message' in data:
                logger.error(f"API Error: {data['Error Message']}")
                return None
            
            if 'Note' in data:
                logger.warning(f"API Note: {data['Note']}")
                return None
            
            return data
            
        except requests.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Get real-time exchange rate between two currencies
        
        Args:
            from_currency: Base currency code (e.g., 'EUR')
            to_currency: Quote currency code (e.g., 'USD')
            
        Returns:
            Dictionary with exchange rate data
        """
        params = {
            'function': 'CURRENCY_EXCHANGE_RATE',
            'from_currency': from_currency,
            'to_currency': to_currency
        }
        
        data = self._make_request(params)
        if not data:
            return None
        
        rate_data = data.get('Realtime Currency Exchange Rate', {})
        
        if not rate_data:
            logger.error(f"No exchange rate data found for {from_currency}/{to_currency}")
            return None
        
        return {
            'pair': f"{from_currency}/{to_currency}",
            'rate': float(rate_data.get('5. Exchange Rate', 0)),
            'bid': float(rate_data.get('8. Bid Price', 0)),
            'ask': float(rate_data.get('9. Ask Price', 0)),
            'timestamp': rate_data.get('6. Last Refreshed', ''),
            'timezone': rate_data.get('7. Time Zone', '')
        }
    
    def get_intraday_data(self, from_currency: str, to_currency: str, 
                         interval: str = '5min', outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """
        Get intraday forex data
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            interval: Time interval ('1min', '5min', '15min', '30min', '60min')
            outputsize: 'compact' (last 100 data points) or 'full' (up to 20 years)
            
        Returns:
            DataFrame with OHLC data
        """
        params = {
            'function': 'FX_INTRADAY',
            'from_symbol': from_currency,
            'to_symbol': to_currency,
            'interval': interval,
            'outputsize': outputsize
        }
        
        data = self._make_request(params)
        if not data:
            return None
        
        # Find the time series key
        time_series_key = None
        for key in data.keys():
            if 'Time Series FX' in key:
                time_series_key = key
                break
        
        if not time_series_key:
            logger.error(f"No time series data found for {from_currency}/{to_currency}")
            return None
        
        time_series = data[time_series_key]
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['Open', 'High', 'Low', 'Close']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_daily_data(self, from_currency: str, to_currency: str, 
                      outputsize: str = 'compact') -> Optional[pd.DataFrame]:
        """
        Get daily forex data
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            outputsize: 'compact' (last 100 data points) or 'full' (up to 20 years)
            
        Returns:
            DataFrame with daily OHLC data
        """
        params = {
            'function': 'FX_DAILY',
            'from_symbol': from_currency,
            'to_symbol': to_currency,
            'outputsize': outputsize
        }
        
        data = self._make_request(params)
        if not data:
            return None
        
        time_series = data.get('Time Series FX (Daily)', {})
        
        if not time_series:
            logger.error(f"No daily data found for {from_currency}/{to_currency}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['Open', 'High', 'Low', 'Close']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_weekly_data(self, from_currency: str, to_currency: str) -> Optional[pd.DataFrame]:
        """
        Get weekly forex data
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            
        Returns:
            DataFrame with weekly OHLC data
        """
        params = {
            'function': 'FX_WEEKLY',
            'from_symbol': from_currency,
            'to_symbol': to_currency
        }
        
        data = self._make_request(params)
        if not data:
            return None
        
        time_series = data.get('Time Series FX (Weekly)', {})
        if not time_series:
            logger.error(f"No weekly data found for {from_currency}/{to_currency}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['Open', 'High', 'Low', 'Close']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_monthly_data(self, from_currency: str, to_currency: str) -> Optional[pd.DataFrame]:
        """
        Get monthly forex data
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            
        Returns:
            DataFrame with monthly OHLC data
        """
        params = {
            'function': 'FX_MONTHLY',
            'from_symbol': from_currency,
            'to_symbol': to_currency
        }
        
        data = self._make_request(params)
        if not data:
            return None
        
        time_series = data.get('Time Series FX (Monthly)', {})
        
        if not time_series:
            logger.error(f"No monthly data found for {from_currency}/{to_currency}")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        
        # Rename columns
        df.columns = ['Open', 'High', 'Low', 'Close']
        
        # Convert to numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    def get_multiple_rates(self, pairs: List[Tuple[str, str]]) -> Dict[str, Dict]:
        """
        Get exchange rates for multiple currency pairs
        
        Args:
            pairs: List of (from_currency, to_currency) tuples
            
        Returns:
            Dictionary with pair names as keys and rate data as values
        """
        rates = {}
        
        for from_currency, to_currency in pairs:
            pair_name = f"{from_currency}/{to_currency}"
            rate_data = self.get_exchange_rate(from_currency, to_currency)
            
            if rate_data:
                rates[pair_name] = rate_data
            else:
                logger.warning(f"Failed to get rate for {pair_name}")
        
        return rates
    
    def get_pair_data_range(self, from_currency: str, to_currency: str, 
                           start_date: datetime, end_date: datetime) -> Optional[pd.DataFrame]:
        """
        Get forex data for a specific date range
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with OHLC data for the specified range
        """
        # Get full daily data
        df = self.get_daily_data(from_currency, to_currency, outputsize='full')
        
        if df is None:
            return None
        
        # Filter by date range
        mask = (df.index >= start_date) & (df.index <= end_date)
        filtered_df = df[mask]
        
        if filtered_df.empty:
            logger.warning(f"No data found for {from_currency}/{to_currency} "
                         f"between {start_date} and {end_date}")
            return None
        
        return filtered_df
    
    def validate_currency_pair(self, from_currency: str, to_currency: str) -> bool:
        """
        Validate if a currency pair is supported
        
        Args:
            from_currency: Base currency code
            to_currency: Quote currency code
            
        Returns:
            True if pair is supported, False otherwise
        """
        # Try to get exchange rate
        rate_data = self.get_exchange_rate(from_currency, to_currency)
        return rate_data is not None
    
    def get_api_status(self) -> Dict:
        """
        Get API status and usage information
        
        Returns:
            Dictionary with API status information
        """
        return {
            'request_count': self.request_count,
            'last_request_time': self.last_request_time,
            'rate_limit_delay': self.rate_limit_delay,
            'api_key_set': bool(self.api_key)
        }
