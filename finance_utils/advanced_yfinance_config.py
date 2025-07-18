#!/usr/bin/env python3
"""
Advanced YFinance Configuration with Multiple Workarounds
"""

import yfinance as yf
import requests
import time
import random
from datetime import datetime, timedelta
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RateLimitBypassYFinance:
    """Advanced Yahoo Finance client with rate limit bypass techniques"""
    
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
        
    def setup_session(self):
        """Configure session with retry strategy and headers"""
        
        # Retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
        ]
        
        self.session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        })
    
    def get_stock_data_with_fallback(self, symbol, period='1y', interval='1d'):
        """Get stock data with multiple fallback methods"""
        
        methods = [
            self._method_direct_yfinance,
            self._method_alternative_endpoints,
            self._method_scraping_fallback,
        ]
        
        for method_name, method in enumerate(methods):
            try:
                print(f"Trying method {method_name + 1}: {method.__name__}")
                data = method(symbol, period, interval)
                if data is not None and not data.empty:
                    print(f"✅ Success with method {method_name + 1}")
                    return data
                else:
                    print(f"❌ Method {method_name + 1} returned empty data")
            except Exception as e:
                print(f"❌ Method {method_name + 1} failed: {e}")
                time.sleep(2)  # Wait between attempts
        
        print("❌ All methods failed")
        return None
    
    def _method_direct_yfinance(self, symbol, period, interval):
        """Method 1: Direct yfinance with custom session"""
        ticker = yf.Ticker(symbol)
        ticker.session = self.session
        
        # Add random delay
        time.sleep(random.uniform(1, 3))
        
        return ticker.history(period=period, interval=interval)
    
    def _method_alternative_endpoints(self, symbol, period, interval):
        """Method 2: Try alternative Yahoo Finance endpoints"""
        
        # Calculate timestamps
        end_time = int(time.time())
        if period == '1y':
            start_time = end_time - (365 * 24 * 60 * 60)
        elif period == '6mo':
            start_time = end_time - (180 * 24 * 60 * 60)
        else:
            start_time = end_time - (30 * 24 * 60 * 60)
        
        # Try different endpoints
        endpoints = [
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
            f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}",
            f"https://finance.yahoo.com/quote/{symbol}/history",
        ]
        
        for endpoint in endpoints:
            try:
                params = {
                    'period1': start_time,
                    'period2': end_time,
                    'interval': interval,
                    'events': 'history',
                    'includeAdjustedClose': 'true'
                }
                
                response = self.session.get(endpoint, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if 'chart' in data and 'result' in data['chart']:
                        return self._parse_yahoo_response(data, symbol)
                        
            except Exception as e:
                print(f"Endpoint {endpoint} failed: {e}")
                continue
        
        return None
    
    def _method_scraping_fallback(self, symbol, period, interval):
        """Method 3: Scraping fallback (basic implementation)"""
        # This would require more complex scraping logic
        # For now, return None as placeholder
        return None
    
    def _parse_yahoo_response(self, data, symbol):
        """Parse Yahoo Finance API response into pandas DataFrame"""
        try:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quote_data = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'Open': quote_data['open'],
                'High': quote_data['high'],
                'Low': quote_data['low'],
                'Close': quote_data['close'],
                'Volume': quote_data['volume'],
            })
            
            # Convert timestamps to datetime
            df.index = pd.to_datetime(timestamps, unit='s')
            
            return df
            
        except Exception as e:
            print(f"Failed to parse Yahoo response: {e}")
            return None

def test_advanced_yfinance():
    """Test the advanced YFinance configuration"""
    
    print("=== Advanced YFinance Rate Limit Bypass Test ===")
    print(f"Current time: {datetime.now()}")
    
    client = RateLimitBypassYFinance()
    
    # Test with a few symbols
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    for symbol in symbols:
        print(f"\n--- Testing {symbol} ---")
        data = client.get_stock_data_with_fallback(symbol, period='1mo')
        
        if data is not None:
            print(f"✅ Got data for {symbol}: {len(data)} rows")
            print(f"Date range: {data.index[0]} to {data.index[-1]}")
            print(f"Latest close: ${data['Close'].iloc[-1]:.2f}")
        else:
            print(f"❌ Failed to get data for {symbol}")
        
        # Wait between symbols
        time.sleep(3)

if __name__ == "__main__":
    test_advanced_yfinance()
