#!/usr/bin/env python3
"""
Alpha Vantage Stock Adapter - Compatible with our Flask Dashboard
Calculates technical indicators manually to work with free tier
"""

import requests
import pandas as pd
import numpy as np
import json
import time
from datetime import datetime
import os
from alpha_vantage.timeseries import TimeSeries

class AlphaVantageStock:
    """Stock class that mimics StockSimple but uses Alpha Vantage data"""
    
    def __init__(self, symbol, api_key=None):
        self.ticker = symbol.upper()
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.history = None
        self.info = {}
        self.rate_limit_delay = 12  # seconds between requests
        
        if self.api_key:
            self.ts = TimeSeries(key=self.api_key, output_format='pandas')
            self._fetch_data()
            self._calculate_indicators()
        else:
            print(f"❌ No API key available for {symbol}")
    
    def _fetch_data(self):
        """Fetch stock data from Alpha Vantage"""
        try:
            print(f"📊 Fetching Alpha Vantage data for {self.ticker}...")
            
            # Get daily data (last 100 days with compact, full history with 'full')
            data, meta_data = self.ts.get_daily(symbol=self.ticker, outputsize='compact')
            
            # Clean up column names to match our expected format
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'Date'
            
            # Sort by date (oldest first for consistency)
            data = data.sort_index()
            
            # Store the data
            self.history = data
            
            # Create basic info
            self.info = {
                'symbol': self.ticker,
                'shortName': self.ticker,
                'longName': f"{self.ticker} Stock",
                'currency': 'USD',
                'exchange': 'NASDAQ',  # Assume NASDAQ for now
                'market': 'us_market',
                'dataSource': 'Alpha Vantage'
            }
            
            print(f"✅ Retrieved {len(data)} days of data for {self.ticker}")
            
        except Exception as e:
            print(f"❌ Error fetching data for {self.ticker}: {e}")
            self.history = pd.DataFrame()
    
    def _calculate_indicators(self):
        """Calculate technical indicators manually"""
        if self.history is None or self.history.empty:
            return
        
        try:
            # Calculate daily returns
            self.history['Daily Return'] = self.history['Close'].pct_change()
            
            # Calculate Simple Moving Averages
            self.history['50MA'] = self.history['Close'].rolling(window=50).mean()
            self.history['200MA'] = self.history['Close'].rolling(window=200).mean()
            
            # Calculate RSI
            self.history['RSI'] = self._calculate_rsi(self.history['Close'])
            
            # Calculate MACD
            macd_data = self._calculate_macd(self.history['Close'])
            self.history['MACD'] = macd_data['macd']
            self.history['Signal'] = macd_data['signal']
            self.history['Histogram'] = macd_data['histogram']
            
            # Calculate Bollinger Bands
            bb_data = self._calculate_bollinger_bands(self.history['Close'])
            self.history['Upper Band'] = bb_data['upper']
            self.history['Lower Band'] = bb_data['lower']
            self.history['Middle Band'] = bb_data['middle']
            
            # Calculate ATR (Average True Range)
            self.history['ATR'] = self._calculate_atr(self.history)
            
            print(f"✅ Calculated technical indicators for {self.ticker}")
            
        except Exception as e:
            print(f"❌ Error calculating indicators for {self.ticker}: {e}")
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI manually"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_macd(self, prices, fast=12, slow=26, signal=9):
        """Calculate MACD manually"""
        ema_fast = prices.ewm(span=fast).mean()
        ema_slow = prices.ewm(span=slow).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }
    
    def _calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """Calculate Bollinger Bands manually"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return {
            'upper': upper_band,
            'lower': lower_band,
            'middle': sma
        }
    
    def _calculate_atr(self, data, period=14):
        """Calculate Average True Range manually"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    def is_valid(self):
        """Check if the stock data is valid"""
        return self.history is not None and not self.history.empty
    
    def today(self):
        """Get the most recent day's data"""
        if not self.is_valid():
            return None
        return self.history.iloc[-1]
    
    def is_bullish(self):
        """Determine if the stock is in a bullish trend"""
        if not self.is_valid():
            return False
        
        latest = self.today()
        
        # Check if price is above both moving averages and 50MA > 200MA
        if pd.isna(latest['50MA']) or pd.isna(latest['200MA']):
            return False
            
        return (latest['Close'] > latest['50MA'] and 
                latest['50MA'] > latest['200MA'] and
                latest['RSI'] < 70)  # Not overbought
    
    def is_bearish(self):
        """Determine if the stock is in a bearish trend"""
        if not self.is_valid():
            return False
        
        latest = self.today()
        
        # Check if price is below both moving averages and 50MA < 200MA
        if pd.isna(latest['50MA']) or pd.isna(latest['200MA']):
            return False
            
        return (latest['Close'] < latest['50MA'] and 
                latest['50MA'] < latest['200MA'] and
                latest['RSI'] > 30)  # Not oversold

class AlphaVantageManager:
    """Manager class to handle multiple Alpha Vantage stocks"""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY')
        self.stocks = {}
        self.request_count = 0
        self.rate_limit_delay = 12
        
        if not self.api_key:
            print("⚠️  No Alpha Vantage API key found. Please set ALPHA_VANTAGE_API_KEY environment variable.")
    
    def get_stock(self, symbol):
        """Get stock data, using cache if available"""
        symbol = symbol.upper()
        
        if symbol not in self.stocks:
            # Rate limiting
            if self.request_count > 0:
                print(f"⏳ Waiting {self.rate_limit_delay} seconds for rate limit...")
                time.sleep(self.rate_limit_delay)
            
            self.stocks[symbol] = AlphaVantageStock(symbol, self.api_key)
            self.request_count += 1
        
        return self.stocks[symbol]
    
    def get_stock_summary(self, symbol):
        """Get stock summary similar to our Flask app format"""
        stock = self.get_stock(symbol)
        
        if not stock.is_valid():
            return None
        
        latest = stock.today()
        
        # Calculate data freshness
        last_date = stock.history.index[-1].date()
        today = datetime.now().date()
        days_behind = (today - last_date).days
        
        return {
            'symbol': stock.ticker,
            'current_price': round(float(latest['Close']), 2),
            'volume': int(latest['Volume']),
            'high': round(float(latest['High']), 2),
            'low': round(float(latest['Low']), 2),
            'rsi': round(float(latest['RSI']), 1) if pd.notna(latest['RSI']) else None,
            'macd': round(float(latest['MACD']), 3) if pd.notna(latest['MACD']) else None,
            'ma_50': round(float(latest['50MA']), 2) if pd.notna(latest['50MA']) else None,
            'ma_200': round(float(latest['200MA']), 2) if pd.notna(latest['200MA']) else None,
            'growth_percent': round(((stock.history["Close"].iloc[-1] - stock.history["Close"].iloc[0]) / stock.history["Close"].iloc[0]) * 100, 2),
            'volatility': round(float(stock.history["Daily Return"].std()), 4),
            'is_bullish': stock.is_bullish(),
            'is_bearish': stock.is_bearish(),
            'last_updated': last_date.strftime('%Y-%m-%d'),
            'days_behind': days_behind,
            'data_points': len(stock.history)
        }
    
    def test_connection(self):
        """Test the Alpha Vantage connection"""
        print("🧪 Testing Alpha Vantage connection...")
        
        if not self.api_key:
            print("❌ No API key available")
            return False
        
        try:
            # Test with AAPL
            test_stock = self.get_stock('AAPL')
            
            if test_stock.is_valid():
                summary = self.get_stock_summary('AAPL')
                print(f"✅ Connection successful!")
                print(f"  AAPL: ${summary['current_price']}")
                print(f"  Data points: {summary['data_points']}")
                print(f"  Last updated: {summary['last_updated']}")
                return True
            else:
                print("❌ Connection failed - no data returned")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

def main():
    """Test the Alpha Vantage adapter"""
    print("🚀 Alpha Vantage Stock Adapter Test")
    print("=" * 40)
    
    # Initialize manager
    manager = AlphaVantageManager()
    
    # Test connection
    if not manager.test_connection():
        print("❌ Failed to connect to Alpha Vantage")
        return
    
    # Test with multiple stocks
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    
    print(f"\n📊 Testing {len(symbols)} stocks...")
    
    for symbol in symbols:
        try:
            summary = manager.get_stock_summary(symbol)
            if summary:
                trend = "Bullish" if summary['is_bullish'] else "Bearish" if summary['is_bearish'] else "Neutral"
                print(f"\n✅ {symbol}: ${summary['current_price']} | {trend} | RSI: {summary['rsi']}")
            else:
                print(f"\n❌ {symbol}: No data available")
                
        except Exception as e:
            print(f"\n❌ {symbol}: Error - {e}")
    
    print(f"\n🎯 Total API requests made: {manager.request_count}")
    print(f"📋 Daily limit remaining: {500 - manager.request_count}")

if __name__ == "__main__":
    main()
