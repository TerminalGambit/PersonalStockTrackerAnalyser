import unittest
from flask import Flask
from app_combined import app

class TestForexAPI(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.app = app.test_client()
        self.app.testing = True

    def test_api_forex_pairs(self):
        response = self.app.get('/api/forex/pairs')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('major', data)
        self.assertIn('minor', data)
        self.assertIn('exotic', data)

    def test_api_forex_rates(self):
        response = self.app.get('/api/forex/rates')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('EUR/USD', data)
        self.assertIn('GBP/USD', data)

    def test_api_forex_overview(self):
        response = self.app.get('/api/forex/overview')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('total_pairs', data)
        self.assertIn('active_sessions', data)

    def test_api_forex_sessions(self):
        response = self.app.get('/api/forex/sessions')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('sydney', data)
        self.assertIn('tokyo', data)

if __name__ == '__main__':
    unittest.main()
