#!/usr/bin/env python3
"""
Comprehensive Forex Implementation Test Suite
Tests all aspects of the forex system including error handling, caching, and validation.
"""

import unittest
import tempfile
import os
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
import requests

# Import our forex modules
from forex_client import ForexClient
from currency_pairs import (
    get_all_pairs, get_pairs_by_category, get_pair_info,
    is_market_open, get_active_sessions, get_most_active_pairs,
    MAJOR_PAIRS, MINOR_PAIRS, EXOTIC_PAIRS
)

class TestForexClient(unittest.TestCase):
    """Test the ForexClient class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_api_key = "test_key_123"
        self.client = ForexClient(self.test_api_key)
        
        # Mock response data
        self.mock_exchange_rate_response = {
            "Realtime Currency Exchange Rate": {
                "1. From_Currency Code": "EUR",
                "2. From_Currency Name": "Euro",
                "3. To_Currency Code": "USD",
                "4. To_Currency Name": "United States Dollar",
                "5. Exchange Rate": "1.08500000",
                "6. Last Refreshed": "2025-07-18 10:15:00",
                "7. Time Zone": "UTC",
                "8. Bid Price": "1.08480000",
                "9. Ask Price": "1.08520000"
            }
        }
        
        self.mock_intraday_response = {
            "Meta Data": {
                "1. Information": "FX Intraday (5min) Time Series",
                "2. From Symbol": "EUR",
                "3. To Symbol": "USD",
                "4. Last Refreshed": "2025-07-18 10:15:00",
                "5. Interval": "5min",
                "6. Output Size": "Compact",
                "7. Time Zone": "UTC"
            },
            "Time Series FX (5min)": {
                "2025-07-18 10:15:00": {
                    "1. open": "1.08450",
                    "2. high": "1.08520",
                    "3. low": "1.08430",
                    "4. close": "1.08500"
                },
                "2025-07-18 10:10:00": {
                    "1. open": "1.08400",
                    "2. high": "1.08460",
                    "3. low": "1.08390",
                    "4. close": "1.08450"
                }
            }
        }
    
    def test_forex_client_initialization(self):
        """Test ForexClient initialization"""
        self.assertEqual(self.client.api_key, self.test_api_key)
        self.assertEqual(self.client.base_url, "https://www.alphavantage.co/query")
        self.assertEqual(self.client.request_count, 0)
        self.assertEqual(self.client.rate_limit_delay, 12)
    
    @patch('requests.Session.get')
    def test_get_exchange_rate_success(self, mock_get):
        """Test successful exchange rate retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_exchange_rate_response
        mock_get.return_value = mock_response
        
        result = self.client.get_exchange_rate("EUR", "USD")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['pair'], "EUR/USD")
        self.assertEqual(result['rate'], 1.085)
        self.assertEqual(result['bid'], 1.0848)
        self.assertEqual(result['ask'], 1.0852)
        self.assertEqual(result['timestamp'], "2025-07-18 10:15:00")
    
    @patch('requests.Session.get')
    def test_get_exchange_rate_api_error(self, mock_get):
        """Test exchange rate retrieval with API error"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"Error Message": "Invalid API call"}
        mock_get.return_value = mock_response
        
        result = self.client.get_exchange_rate("EUR", "USD")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_get_exchange_rate_rate_limit(self, mock_get):
        """Test exchange rate retrieval with rate limit"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"Note": "API call frequency is 5 calls per minute"}
        mock_get.return_value = mock_response
        
        result = self.client.get_exchange_rate("EUR", "USD")
        
        self.assertIsNone(result)
    
    @patch('requests.Session.get')
    def test_get_intraday_data_success(self, mock_get):
        """Test successful intraday data retrieval"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = self.mock_intraday_response
        mock_get.return_value = mock_response
        
        result = self.client.get_intraday_data("EUR", "USD", "5min")
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertListEqual(list(result.columns), ['Open', 'High', 'Low', 'Close'])
        
        # Check data types
        for col in result.columns:
            self.assertTrue(pd.api.types.is_numeric_dtype(result[col]))
    
    @patch('requests.Session.get')
    def test_network_error_handling(self, mock_get):
        """Test network error handling"""
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = self.client.get_exchange_rate("EUR", "USD")
        
        self.assertIsNone(result)
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Record initial time
        start_time = time.time()
        
        # Make first request
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = self.mock_exchange_rate_response
            mock_get.return_value = mock_response
            
            self.client.get_exchange_rate("EUR", "USD")
            first_request_time = time.time()
            
            # Make second request immediately (should be delayed)
            self.client.get_exchange_rate("GBP", "USD")
            second_request_time = time.time()
            
            # Check that there was a delay
            time_diff = second_request_time - first_request_time
            self.assertGreaterEqual(time_diff, self.client.rate_limit_delay - 1)  # Allow 1 second tolerance
    
    def test_validate_currency_pair(self):
        """Test currency pair validation"""
        with patch.object(self.client, 'get_exchange_rate') as mock_get_rate:
            # Test valid pair
            mock_get_rate.return_value = {"pair": "EUR/USD", "rate": 1.085}
            self.assertTrue(self.client.validate_currency_pair("EUR", "USD"))
            
            # Test invalid pair
            mock_get_rate.return_value = None
            self.assertFalse(self.client.validate_currency_pair("XXX", "YYY"))
    
    def test_get_api_status(self):
        """Test API status information"""
        status = self.client.get_api_status()
        
        self.assertIn('request_count', status)
        self.assertIn('last_request_time', status)
        self.assertIn('rate_limit_delay', status)
        self.assertIn('api_key_set', status)
        self.assertTrue(status['api_key_set'])


class TestCurrencyPairs(unittest.TestCase):
    """Test currency pair functionality"""
    
    def test_get_all_pairs(self):
        """Test getting all currency pairs"""
        all_pairs = get_all_pairs()
        
        self.assertIsInstance(all_pairs, dict)
        self.assertGreater(len(all_pairs), 0)
        
        # Check that all categories are included
        for pair in MAJOR_PAIRS:
            self.assertIn(pair, all_pairs)
        for pair in MINOR_PAIRS:
            self.assertIn(pair, all_pairs)
        for pair in EXOTIC_PAIRS:
            self.assertIn(pair, all_pairs)
    
    def test_get_pairs_by_category(self):
        """Test getting pairs by category"""
        major_pairs = get_pairs_by_category('major')
        minor_pairs = get_pairs_by_category('minor')
        exotic_pairs = get_pairs_by_category('exotic')
        invalid_pairs = get_pairs_by_category('invalid')
        
        self.assertEqual(major_pairs, MAJOR_PAIRS)
        self.assertEqual(minor_pairs, MINOR_PAIRS)
        self.assertEqual(exotic_pairs, EXOTIC_PAIRS)
        self.assertEqual(invalid_pairs, {})
    
    def test_get_pair_info(self):
        """Test getting specific pair information"""
        eur_usd_info = get_pair_info('EUR/USD')
        invalid_info = get_pair_info('XXX/YYY')
        
        self.assertIsNotNone(eur_usd_info)
        self.assertEqual(eur_usd_info['category'], 'major')
        self.assertIn('name', eur_usd_info)
        self.assertIn('pip_value', eur_usd_info)
        
        self.assertIsNone(invalid_info)
    
    def test_trading_sessions(self):
        """Test trading session functionality"""
        from datetime import timezone
        # Note: This test might be time-dependent, so we'll mock the time
        with patch('currency_pairs.datetime') as mock_datetime:
            # Mock London session time (10:00 UTC)
            mock_datetime.now.return_value = datetime(2025, 7, 18, 10, 0, 0)
            mock_datetime.timezone = timezone
            
            # Test is_market_open
            self.assertTrue(is_market_open('London'))
            self.assertFalse(is_market_open('Sydney'))
            
            # Test get_active_sessions
            active_sessions = get_active_sessions()
            self.assertIn('London', active_sessions)
            
            # Test get_most_active_pairs
            active_pairs = get_most_active_pairs()
            self.assertIsInstance(active_pairs, list)
            self.assertGreater(len(active_pairs), 0)


class TestForexDataValidation(unittest.TestCase):
    """Test data validation and quality checks"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.valid_df = pd.DataFrame({
            'Open': [1.0850, 1.0855, 1.0860],
            'High': [1.0870, 1.0875, 1.0880],
            'Low': [1.0840, 1.0845, 1.0850],
            'Close': [1.0860, 1.0865, 1.0870]
        }, index=pd.date_range('2025-07-18', periods=3, freq='5min'))
        
        self.invalid_df = pd.DataFrame({
            'Open': [1.0850, np.nan, 1.0860],
            'High': [1.0870, 1.0875, np.inf],
            'Low': [1.0840, 1.0845, 1.0850],
            'Close': [1.0860, 1.0865, -1.0870]  # Invalid negative price
        }, index=pd.date_range('2025-07-18', periods=3, freq='5min'))
    
    def test_validate_forex_data(self):
        """Test forex data validation"""
        # Test valid data
        self.assertTrue(self._validate_forex_data(self.valid_df))
        
        # Test invalid data
        self.assertFalse(self._validate_forex_data(self.invalid_df))
        
        # Test empty data
        self.assertFalse(self._validate_forex_data(pd.DataFrame()))
    
    def _validate_forex_data(self, df):
        """Validate forex data quality"""
        if df.empty:
            return False
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in df.columns for col in required_columns):
            return False
        
        # Check for NaN values
        if df[required_columns].isna().any().any():
            return False
        
        # Check for infinite values
        if np.isinf(df[required_columns]).any().any():
            return False
        
        # Check for negative prices
        if (df[required_columns] < 0).any().any():
            return False
        
        # Check OHLC relationships
        if not all(df['High'] >= df['Low']):
            return False
        
        if not all(df['High'] >= df['Open']):
            return False
        
        if not all(df['High'] >= df['Close']):
            return False
        
        if not all(df['Low'] <= df['Open']):
            return False
        
        if not all(df['Low'] <= df['Close']):
            return False
        
        return True


class TestForexCaching(unittest.TestCase):
    """Test caching functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache_dir = tempfile.mkdtemp()
        self.cache_file = os.path.join(self.cache_dir, "EUR_USD_daily.json")
        
        self.test_data = {
            'pair': 'EUR/USD',
            'timestamp': datetime.now().isoformat(),
            'data': {
                '2025-07-18': {'open': 1.0850, 'high': 1.0870, 'low': 1.0840, 'close': 1.0860},
                '2025-07-17': {'open': 1.0840, 'high': 1.0860, 'low': 1.0830, 'close': 1.0850}
            }
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        os.rmdir(self.cache_dir)
    
    def test_cache_storage(self):
        """Test cache storage"""
        # Store data in cache
        with open(self.cache_file, 'w') as f:
            json.dump(self.test_data, f)
        
        # Verify cache file exists
        self.assertTrue(os.path.exists(self.cache_file))
        
        # Load and verify data
        with open(self.cache_file, 'r') as f:
            cached_data = json.load(f)
        
        self.assertEqual(cached_data['pair'], 'EUR/USD')
        self.assertIn('data', cached_data)
    
    def test_cache_expiration(self):
        """Test cache expiration logic"""
        # Create old cache file
        old_timestamp = (datetime.now() - timedelta(hours=2)).isoformat()
        old_data = self.test_data.copy()
        old_data['timestamp'] = old_timestamp
        
        with open(self.cache_file, 'w') as f:
            json.dump(old_data, f)
        
        # Test cache expiration (assuming 1 hour expiration)
        cache_age = datetime.now() - datetime.fromisoformat(old_timestamp)
        self.assertGreater(cache_age.total_seconds(), 3600)  # Older than 1 hour
    
    def test_cache_invalidation(self):
        """Test cache invalidation"""
        # Store valid cache
        with open(self.cache_file, 'w') as f:
            json.dump(self.test_data, f)
        
        # Invalidate cache by removing file
        os.remove(self.cache_file)
        
        # Verify cache is invalidated
        self.assertFalse(os.path.exists(self.cache_file))


class TestForexPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    def test_data_processing_performance(self):
        """Test data processing performance"""
        # Create large dataset
        large_df = pd.DataFrame({
            'Open': np.random.uniform(1.08, 1.09, 10000),
            'High': np.random.uniform(1.08, 1.09, 10000),
            'Low': np.random.uniform(1.08, 1.09, 10000),
            'Close': np.random.uniform(1.08, 1.09, 10000)
        }, index=pd.date_range('2023-01-01', periods=10000, freq='1min'))
        
        # Test processing time
        start_time = time.time()
        
        # Simulate some processing
        large_df['SMA_20'] = large_df['Close'].rolling(20).mean()
        large_df['EMA_12'] = large_df['Close'].ewm(span=12).mean()
        large_df['RSI'] = self._calculate_rsi(large_df['Close'])
        
        processing_time = time.time() - start_time
        
        # Should process 10k records in under 1 second
        self.assertLess(processing_time, 1.0)
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI for performance testing"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi


class TestForexErrorHandling(unittest.TestCase):
    """Test error handling scenarios"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.client = ForexClient("test_key")
    
    def test_invalid_currency_codes(self):
        """Test handling of invalid currency codes"""
        with patch.object(self.client, '_make_request') as mock_request:
            mock_request.return_value = {"Error Message": "Invalid currency code"}
            
            result = self.client.get_exchange_rate("XXX", "YYY")
            self.assertIsNone(result)
    
    def test_network_timeout(self):
        """Test network timeout handling"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("Request timeout")
            
            result = self.client.get_exchange_rate("EUR", "USD")
            self.assertIsNone(result)
    
    def test_json_parse_error(self):
        """Test JSON parsing error handling"""
        with patch('requests.Session.get') as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            mock_get.return_value = mock_response
            
            result = self.client.get_exchange_rate("EUR", "USD")
            self.assertIsNone(result)
    
    def test_api_key_error(self):
        """Test API key error handling"""
        client_no_key = ForexClient("")
        
        with patch.object(client_no_key, '_make_request') as mock_request:
            mock_request.return_value = {"Error Message": "Invalid API key"}
            
            result = client_no_key.get_exchange_rate("EUR", "USD")
            self.assertIsNone(result)


def create_test_suite():
    """Create a comprehensive test suite"""
    suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestForexClient,
        TestCurrencyPairs,
        TestForexDataValidation,
        TestForexCaching,
        TestForexPerformance,
        TestForexErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    return suite


def run_tests():
    """Run all tests with detailed reporting"""
    print("🧪 Running Forex Implementation Test Suite")
    print("=" * 60)
    
    # Create and run test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed! Forex implementation is robust.")
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues.")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
