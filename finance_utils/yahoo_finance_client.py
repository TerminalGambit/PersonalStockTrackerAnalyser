import requests
import time
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class YahooFinanceClient:
    """
    A robust Yahoo Finance client that handles rate limiting, authentication, and retries.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.crumb = None
        self.last_crumb_time = None
        self.crumb_expires_hours = 6  # Refresh crumb every 6 hours
        self.base_delay = 1  # Base delay between requests in seconds
        self.max_retries = 3
        
        # Set a realistic User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def _needs_new_crumb(self) -> bool:
        """Check if we need to fetch a new crumb."""
        if not self.crumb or not self.last_crumb_time:
            return True
        
        time_since_crumb = datetime.now() - self.last_crumb_time
        return time_since_crumb > timedelta(hours=self.crumb_expires_hours)
    
    def _fetch_crumb(self) -> bool:
        """Fetch a fresh crumb and session cookies from Yahoo Finance."""
        try:
            logger.info("Fetching new crumb from Yahoo Finance...")
            
            # First, get the main page to establish session
            response = self.session.get('https://finance.yahoo.com/', timeout=10)
            response.raise_for_status()
            
            # Then get a quote page to get the crumb
            response = self.session.get('https://finance.yahoo.com/quote/AAPL/history', timeout=10)
            response.raise_for_status()
            
            # Extract crumb from the HTML
            crumb_match = re.search(r'"CrumbStore":\{"crumb":"([^"]+)"\}', response.text)
            if not crumb_match:
                logger.error("Could not find crumb in response")
                return False
            
            self.crumb = crumb_match.group(1)
            self.last_crumb_time = datetime.now()
            logger.info(f"Successfully fetched new crumb: {self.crumb[:10]}...")
            
            return True
            
        except Exception as e:
            logger.error(f"Error fetching crumb: {str(e)}")
            return False
    
    def _make_request(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Make a request with retry logic and rate limiting."""
        if params is None:
            params = {}
        
        # Add crumb to params if we have one
        if self.crumb:
            params['crumb'] = self.crumb
        
        for attempt in range(self.max_retries):
            try:
                # Add exponential backoff with jitter
                if attempt > 0:
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    logger.info(f"Retrying in {delay:.2f} seconds (attempt {attempt + 1}/{self.max_retries})...")
                    time.sleep(delay)
                
                # Make the request
                response = self.session.get(url, params=params, timeout=10)
                
                # Handle rate limiting
                if response.status_code == 429:
                    logger.warning("Rate limited by Yahoo Finance")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.base_delay * (2 ** (attempt + 1)))
                        continue
                    else:
                        logger.error("Max retries exceeded due to rate limiting")
                        return None
                
                # Handle unauthorized (invalid crumb)
                if response.status_code == 401:
                    logger.warning("Unauthorized - fetching new crumb...")
                    if self._fetch_crumb():
                        params['crumb'] = self.crumb
                        continue
                    else:
                        logger.error("Failed to fetch new crumb")
                        return None
                
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                # Check for Yahoo Finance error responses
                if 'finance' in data and 'error' in data['finance'] and data['finance']['error']:
                    error_code = data['finance']['error'].get('code', 'Unknown')
                    error_desc = data['finance']['error'].get('description', 'Unknown error')
                    
                    if error_code == 'Unauthorized':
                        logger.warning("Invalid crumb detected - refreshing...")
                        if self._fetch_crumb():
                            params['crumb'] = self.crumb
                            continue
                    
                    logger.error(f"Yahoo Finance API error: {error_code} - {error_desc}")
                    return None
                
                # Add a small delay to be respectful
                time.sleep(self.base_delay)
                return data
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Max retries exceeded")
                    return None
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON response (attempt {attempt + 1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    logger.error("Max retries exceeded")
                    return None
        
        return None
    
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current quote data for a symbol."""
        # Ensure we have a valid crumb
        if self._needs_new_crumb():
            if not self._fetch_crumb():
                logger.error("Failed to fetch crumb for quote request")
                return None
        
        url = 'https://query1.finance.yahoo.com/v7/finance/quote'
        params = {
            'symbols': symbol,
            'formatted': 'false'
        }
        
        return self._make_request(url, params)
    
    def get_quote_summary(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive quote summary data for a symbol."""
        # Ensure we have a valid crumb
        if self._needs_new_crumb():
            if not self._fetch_crumb():
                logger.error("Failed to fetch crumb for quote summary request")
                return None
        
        url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/' + symbol
        params = {
            'modules': 'financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail',
            'corsDomain': 'finance.yahoo.com',
            'formatted': 'false'
        }
        
        return self._make_request(url, params)
    
    def get_historical_data(self, symbol: str, period1: int, period2: int, interval: str = '1d') -> Optional[Dict[str, Any]]:
        """Get historical data for a symbol."""
        # Ensure we have a valid crumb
        if self._needs_new_crumb():
            if not self._fetch_crumb():
                logger.error("Failed to fetch crumb for historical data request")
                return None
        
        url = 'https://query1.finance.yahoo.com/v7/finance/download/' + symbol
        params = {
            'period1': period1,
            'period2': period2,
            'interval': interval,
            'events': 'history',
            'includeAdjustedClose': 'true'
        }
        
        return self._make_request(url, params)


# Global instance
yahoo_client = YahooFinanceClient()
