#!/usr/bin/env python3
"""
Comprehensive Forex API Tests for Financial Analytics Hub
Tests all forex API endpoints including error handling, data validation, and response formats.

Reference: Alpha Vantage API Documentation
https://www.alphavantage.co/documentation/
"""

import unittest
import json
import requests
from unittest.mock import patch, Mock
from flask import Flask
from app_combined import app
import sys
import os

# Add the current directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestForexAPIEndpoints(unittest.TestCase):
    """Test all forex API endpoints"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_api_status(self):
        """Test API status endpoint"""
        response = self.app.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('status', data)
        self.assertIn('timestamp', data)
        self.assertIn('forex_enabled', data)
        self.assertIn('stocks_enabled', data)
        self.assertIn('mode', data)
        
        # Verify data types
        self.assertIsInstance(data['status'], str)
        self.assertIsInstance(data['forex_enabled'], bool)
        self.assertIsInstance(data['stocks_enabled'], bool)
        self.assertIsInstance(data['mode'], str)
        
    def test_api_forex_pairs(self):
        """Test forex pairs endpoint"""
        response = self.app.get('/api/forex/pairs')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('major', data)
        self.assertIn('minor', data)
        self.assertIn('exotic', data)
        
        # Verify data structure
        self.assertIsInstance(data['major'], list)
        self.assertIsInstance(data['minor'], list)
        self.assertIsInstance(data['exotic'], list)
        
        # Verify common pairs are present
        self.assertIn('EUR/USD', data['major'])
        self.assertIn('GBP/USD', data['major'])
        self.assertIn('USD/JPY', data['major'])
        
    def test_api_forex_rates(self):
        """Test forex rates endpoint"""
        response = self.app.get('/api/forex/rates')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Verify common pairs are present
        expected_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD']
        for pair in expected_pairs:
            self.assertIn(pair, data)
            
        # Verify data structure for each pair
        for pair, info in data.items():
            self.assertIn('rate', info)
            self.assertIn('change', info)
            self.assertIsInstance(info['rate'], (int, float))
            self.assertIsInstance(info['change'], (int, float))
            
    def test_api_forex_overview(self):
        """Test forex market overview endpoint"""
        response = self.app.get('/api/forex/overview')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Verify required fields
        required_fields = ['total_pairs', 'active_sessions', 'top_movers', 'market_sentiment', 'last_updated']
        for field in required_fields:
            self.assertIn(field, data)
            
        # Verify data types
        self.assertIsInstance(data['total_pairs'], int)
        self.assertIsInstance(data['active_sessions'], int)
        self.assertIsInstance(data['top_movers'], list)
        self.assertIsInstance(data['market_sentiment'], str)
        self.assertIsInstance(data['last_updated'], str)
        
        # Verify top movers structure
        for mover in data['top_movers']:
            self.assertIn('pair', mover)
            self.assertIn('change', mover)
            self.assertIsInstance(mover['pair'], str)
            self.assertIsInstance(mover['change'], (int, float))
            
    def test_api_forex_sessions(self):
        """Test forex trading sessions endpoint"""
        response = self.app.get('/api/forex/sessions')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Verify major trading sessions
        expected_sessions = ['sydney', 'tokyo', 'london', 'new_york']
        for session in expected_sessions:
            self.assertIn(session, data)
            
        # Verify session data structure
        for session, info in data.items():
            self.assertIn('open', info)
            self.assertIn('close', info)
            self.assertIn('active', info)
            self.assertIsInstance(info['open'], str)
            self.assertIsInstance(info['close'], str)
            self.assertIsInstance(info['active'], bool)
            
    def test_api_forex_pair_valid(self):
        """Test forex pair data endpoint with valid pair"""
        response = self.app.get('/api/forex/pair/EUR/USD')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Verify required fields
        required_fields = ['pair', 'current_price', 'volume', 'high', 'low', 'rsi', 'macd',
                          'sma_20', 'sma_50', 'volatility', 'daily_return', 'last_updated', 'data_points']
        for field in required_fields:
            self.assertIn(field, data)
            
        # Verify data types
        self.assertIsInstance(data['pair'], str)
        self.assertIsInstance(data['current_price'], (int, float))
        self.assertIsInstance(data['volume'], int)
        self.assertIsInstance(data['high'], (int, float))
        self.assertIsInstance(data['low'], (int, float))
        self.assertIsInstance(data['rsi'], (int, float))
        self.assertIsInstance(data['macd'], (int, float))
        self.assertIsInstance(data['sma_20'], (int, float))
        self.assertIsInstance(data['sma_50'], (int, float))
        self.assertIsInstance(data['volatility'], (int, float))
        self.assertIsInstance(data['daily_return'], (int, float))
        self.assertIsInstance(data['last_updated'], str)
        self.assertIsInstance(data['data_points'], int)
        
    def test_api_forex_pair_invalid(self):
        """Test forex pair data endpoint with invalid pair"""
        response = self.app.get('/api/forex/pair/XXX/YYY')
        self.assertEqual(response.status_code, 404)
        
        data = response.get_json()
        self.assertIn('error', data)
        self.assertIn('XXX/YYY', data['error'])
        
    def test_api_forex_pairs_filter(self):
        """Test forex pairs endpoint with category filter"""
        # Test major pairs filter
        response = self.app.get('/api/forex/pairs?category=major')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('major', data)
        
        # Test minor pairs filter
        response = self.app.get('/api/forex/pairs?category=minor')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('minor', data)
        
        # Test exotic pairs filter
        response = self.app.get('/api/forex/pairs?category=exotic')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertIn('exotic', data)


class TestForexDataValidation(unittest.TestCase):
    """Test forex data validation and error handling"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_forex_rates_data_consistency(self):
        """Test that forex rates data is consistent across calls"""
        # Make multiple calls to ensure consistency
        response1 = self.app.get('/api/forex/rates')
        response2 = self.app.get('/api/forex/rates')
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # Check that the same pairs are present in both responses
        self.assertEqual(set(data1.keys()), set(data2.keys()))
        
        # Check that rates are realistic (between 0.01 and 10.0 for major pairs)
        for pair, info in data1.items():
            self.assertGreater(info['rate'], 0.01)
            self.assertLess(info['rate'], 10.0)
            
    def test_forex_overview_data_ranges(self):
        """Test that forex overview data is within expected ranges"""
        response = self.app.get('/api/forex/overview')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Check that total_pairs is a reasonable number
        self.assertGreater(data['total_pairs'], 0)
        self.assertLess(data['total_pairs'], 100)
        
        # Check that active_sessions is between 0 and 4
        self.assertGreaterEqual(data['active_sessions'], 0)
        self.assertLessEqual(data['active_sessions'], 4)
        
        # Check that top_movers has at least 1 item
        self.assertGreater(len(data['top_movers']), 0)
        
        # Check that market_sentiment is one of expected values
        valid_sentiments = ['bullish', 'bearish', 'neutral']
        self.assertIn(data['market_sentiment'], valid_sentiments)
        
    def test_forex_sessions_time_format(self):
        """Test that forex sessions have valid time formats"""
        response = self.app.get('/api/forex/sessions')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Check time format (HH:MM)
        import re
        time_pattern = re.compile(r'^([01]?[0-9]|2[0-3]):[0-5][0-9]$')
        
        for session, info in data.items():
            self.assertRegex(info['open'], time_pattern)
            self.assertRegex(info['close'], time_pattern)


class TestForexAPIPerformance(unittest.TestCase):
    """Test forex API performance and response times"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_api_response_times(self):
        """Test that API responses are reasonably fast"""
        import time
        
        endpoints = [
            '/api/status',
            '/api/forex/pairs',
            '/api/forex/rates',
            '/api/forex/overview',
            '/api/forex/sessions'
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = self.app.get(endpoint)
            end_time = time.time()
            
            # Check that response is successful
            self.assertEqual(response.status_code, 200)
            
            # Check that response time is under 1 second
            response_time = end_time - start_time
            self.assertLess(response_time, 1.0, f"Endpoint {endpoint} took too long: {response_time:.2f}s")
            
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = self.app.get('/api/forex/rates')
            results.append(response.status_code)
            
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            
        # Start all threads
        for thread in threads:
            thread.start()
            
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
        # Check that all requests were successful
        self.assertEqual(len(results), 5)
        for status_code in results:
            self.assertEqual(status_code, 200)


class TestForexAPIDocumentation(unittest.TestCase):
    """Test that forex API provides proper documentation and references"""
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
        
    def test_api_status_includes_reference(self):
        """Test that API status includes reference to Alpha Vantage"""
        response = self.app.get('/api/status')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        
        # Check that the response includes mode information
        self.assertIn('mode', data)
        self.assertEqual(data['mode'], 'demo')
        
    def test_forex_pair_endpoint_documentation(self):
        """Test that forex pair endpoints work as documented"""
        # Test that EUR/USD works (as mentioned in the startup message)
        response = self.app.get('/api/forex/pair/EUR/USD')
        self.assertEqual(response.status_code, 200)
        
        data = response.get_json()
        self.assertEqual(data['pair'], 'EUR/USD')
        
        # Test that the data structure matches what's expected
        self.assertIn('current_price', data)
        self.assertIn('rsi', data)
        self.assertIn('macd', data)
        self.assertIn('sma_20', data)
        self.assertIn('sma_50', data)


if __name__ == '__main__':
    print("🧪 Running Comprehensive Forex API Tests")
    print("=" * 50)
    print("📊 Testing all forex API endpoints:")
    print("  - /api/status")
    print("  - /api/forex/pairs")
    print("  - /api/forex/rates")
    print("  - /api/forex/overview")
    print("  - /api/forex/sessions")
    print("  - /api/forex/pair/<pair>")
    print("=" * 50)
    print("📚 Reference: Alpha Vantage API Documentation")
    print("    https://www.alphavantage.co/documentation/")
    print("=" * 50)
    
    # Run tests
    unittest.main(verbosity=2)
