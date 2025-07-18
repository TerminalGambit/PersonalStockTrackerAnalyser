#!/usr/bin/env python3
"""
Alpha Vantage API Explorer and Integration
Free tier: 500 requests/day, 5 requests/minute
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators
import os

class AlphaVantageExplorer:
    def __init__(self, api_key=None):
        """
        Initialize Alpha Vantage Explorer
        Get free API key from: https://www.alphavantage.co/support/#api-key
        """
        self.api_key = api_key or self.get_api_key()
        self.base_url = "https://www.alphavantage.co/query"
        self.request_count = 0
        self.rate_limit_delay = 12  # seconds between requests (5 requests/minute)
        
        if self.api_key:
            self.ts = TimeSeries(key=self.api_key, output_format='pandas')
            self.ti = TechIndicators(key=self.api_key, output_format='pandas')
        else:
            print("⚠️  No API key provided. You'll need to get one from alphavantage.co")
    
    def get_api_key(self):
        """Get API key from environment or user input"""
        # Check environment variable first
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        if api_key:
            return api_key
        
        # Ask user for API key
        print("🔑 Alpha Vantage API Key Setup")
        print("=" * 40)
        print("1. Go to https://www.alphavantage.co/support/#api-key")
        print("2. Enter your email and get a free API key")
        print("3. Copy the API key and paste it below")
        print()
        
        api_key = input("Enter your Alpha Vantage API key (or press Enter to skip): ").strip()
        
        if api_key:
            # Save to environment file for future use
            with open('.env', 'a') as f:
                f.write(f"\nALPHA_VANTAGE_API_KEY={api_key}\n")
            print("✅ API key saved to .env file")
            return api_key
        
        return None
    
    def wait_for_rate_limit(self):
        """Wait for rate limit if needed"""
        if self.request_count > 0:
            print(f"⏳ Waiting {self.rate_limit_delay} seconds for rate limit...")
            time.sleep(self.rate_limit_delay)
        self.request_count += 1
    
    def get_stock_data(self, symbol, outputsize='compact'):
        """
        Get daily stock data
        outputsize: 'compact' (last 100 days) or 'full' (20+ years)
        """
        if not self.api_key:
            print("❌ No API key available")
            return None
            
        try:
            print(f"📊 Fetching data for {symbol}...")
            self.wait_for_rate_limit()
            
            # Get daily data
            data, meta_data = self.ts.get_daily(symbol=symbol, outputsize=outputsize)
            
            # Clean up column names
            data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            data.index.name = 'Date'
            
            # Sort by date (newest first)
            data = data.sort_index()
            
            print(f"✅ Retrieved {len(data)} days of data for {symbol}")
            return data
            
        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return None
    
    def get_technical_indicators(self, symbol, data_length=100):
        """Get technical indicators for a symbol"""
        if not self.api_key:
            print("❌ No API key available")
            return {}
            
        indicators = {}
        
        try:
            # RSI
            print(f"📈 Fetching RSI for {symbol}...")
            self.wait_for_rate_limit()
            rsi_data, _ = self.ti.get_rsi(symbol=symbol, interval='daily', time_period=14)
            indicators['RSI'] = rsi_data['RSI'].sort_index()
            
            # MACD
            print(f"📈 Fetching MACD for {symbol}...")
            self.wait_for_rate_limit()
            macd_data, _ = self.ti.get_macd(symbol=symbol, interval='daily')
            indicators['MACD'] = macd_data['MACD'].sort_index()
            indicators['MACD_Signal'] = macd_data['MACD_Signal'].sort_index()
            indicators['MACD_Hist'] = macd_data['MACD_Hist'].sort_index()
            
            # Simple Moving Averages
            print(f"📈 Fetching SMA 50 for {symbol}...")
            self.wait_for_rate_limit()
            sma50_data, _ = self.ti.get_sma(symbol=symbol, interval='daily', time_period=50)
            indicators['SMA_50'] = sma50_data['SMA'].sort_index()
            
            print(f"📈 Fetching SMA 200 for {symbol}...")
            self.wait_for_rate_limit()
            sma200_data, _ = self.ti.get_sma(symbol=symbol, interval='daily', time_period=200)
            indicators['SMA_200'] = sma200_data['SMA'].sort_index()
            
            # Bollinger Bands
            print(f"📈 Fetching Bollinger Bands for {symbol}...")
            self.wait_for_rate_limit()
            bb_data, _ = self.ti.get_bbands(symbol=symbol, interval='daily')
            indicators['BB_Upper'] = bb_data['Real Upper Band'].sort_index()
            indicators['BB_Lower'] = bb_data['Real Lower Band'].sort_index()
            indicators['BB_Middle'] = bb_data['Real Middle Band'].sort_index()
            
            print(f"✅ Retrieved technical indicators for {symbol}")
            return indicators
            
        except Exception as e:
            print(f"❌ Error fetching technical indicators for {symbol}: {e}")
            return {}
    
    def create_stock_analysis(self, symbol):
        """Create comprehensive stock analysis similar to StockSimple"""
        print(f"\n🔍 Creating comprehensive analysis for {symbol}")
        print("=" * 50)
        
        # Get stock data
        stock_data = self.get_stock_data(symbol)
        if stock_data is None:
            return None
        
        # Get technical indicators
        indicators = self.get_technical_indicators(symbol)
        
        # Combine data
        combined_data = stock_data.copy()
        
        # Add indicators to the main dataframe
        for indicator_name, indicator_data in indicators.items():
            # Align indices and add to combined data
            combined_data = combined_data.join(indicator_data.rename(indicator_name), how='left')
        
        # Calculate additional metrics
        combined_data['Daily_Return'] = combined_data['Close'].pct_change()
        combined_data['Volatility'] = combined_data['Daily_Return'].rolling(window=20).std()
        
        # Create analysis summary
        latest = combined_data.iloc[-1]
        
        summary = {
            'symbol': symbol,
            'date': combined_data.index[-1].strftime('%Y-%m-%d'),
            'current_price': round(float(latest['Close']), 2),
            'volume': int(latest['Volume']),
            'high': round(float(latest['High']), 2),
            'low': round(float(latest['Low']), 2),
            'daily_change': round(float(latest['Daily_Return'] * 100), 2),
            'volatility': round(float(latest['Volatility']), 4),
            'rsi': round(float(latest['RSI']), 1) if 'RSI' in latest and pd.notna(latest['RSI']) else None,
            'macd': round(float(latest['MACD']), 3) if 'MACD' in latest and pd.notna(latest['MACD']) else None,
            'sma_50': round(float(latest['SMA_50']), 2) if 'SMA_50' in latest and pd.notna(latest['SMA_50']) else None,
            'sma_200': round(float(latest['SMA_200']), 2) if 'SMA_200' in latest and pd.notna(latest['SMA_200']) else None,
            'bb_upper': round(float(latest['BB_Upper']), 2) if 'BB_Upper' in latest and pd.notna(latest['BB_Upper']) else None,
            'bb_lower': round(float(latest['BB_Lower']), 2) if 'BB_Lower' in latest and pd.notna(latest['BB_Lower']) else None,
            'data_points': len(combined_data)
        }
        
        # Add trend analysis
        if summary['sma_50'] and summary['sma_200']:
            summary['is_bullish'] = summary['current_price'] > summary['sma_50'] and summary['sma_50'] > summary['sma_200']
            summary['is_bearish'] = summary['current_price'] < summary['sma_50'] and summary['sma_50'] < summary['sma_200']
        else:
            summary['is_bullish'] = False
            summary['is_bearish'] = False
        
        return {
            'summary': summary,
            'data': combined_data,
            'raw_data': stock_data,
            'indicators': indicators
        }
    
    def compare_with_yahoo_finance(self, symbol):
        """Compare Alpha Vantage data with Yahoo Finance (if available)"""
        print(f"\n🔄 Comparing Alpha Vantage vs Yahoo Finance for {symbol}")
        print("=" * 50)
        
        # Get Alpha Vantage data
        av_analysis = self.create_stock_analysis(symbol)
        if not av_analysis:
            print("❌ Failed to get Alpha Vantage data")
            return
        
        av_summary = av_analysis['summary']
        
        # Try to get Yahoo Finance data (using our working advanced config)
        try:
            from advanced_yfinance_config import RateLimitBypassYFinance
            
            yf_client = RateLimitBypassYFinance()
            yf_data = yf_client.get_stock_data_with_fallback(symbol, period='1mo')
            
            if yf_data is not None and not yf_data.empty:
                yf_latest = yf_data.iloc[-1]
                
                print("📊 Data Comparison:")
                print(f"Alpha Vantage - Price: ${av_summary['current_price']}, Date: {av_summary['date']}")
                print(f"Yahoo Finance - Price: ${yf_latest['Close']:.2f}, Date: {yf_data.index[-1].strftime('%Y-%m-%d')}")
                
                price_diff = abs(av_summary['current_price'] - yf_latest['Close'])
                print(f"Price difference: ${price_diff:.2f}")
                
                if price_diff < 1.0:
                    print("✅ Data matches well!")
                else:
                    print("⚠️  Significant price difference - check data sources")
            else:
                print("❌ Yahoo Finance data not available (rate limited)")
                
        except Exception as e:
            print(f"❌ Error comparing with Yahoo Finance: {e}")
        
        # Display Alpha Vantage summary
        print("\n📈 Alpha Vantage Summary:")
        for key, value in av_summary.items():
            print(f"  {key}: {value}")
    
    def test_api_limits(self):
        """Test API rate limits and functionality"""
        print("🧪 Testing Alpha Vantage API Limits")
        print("=" * 40)
        
        if not self.api_key:
            print("❌ No API key available for testing")
            return
        
        print(f"API Key: {self.api_key[:8]}...")
        print(f"Rate limit: {self.rate_limit_delay} seconds between requests")
        print(f"Daily limit: 500 requests")
        
        # Test with a simple request
        try:
            print("\n🔍 Testing basic API functionality...")
            data = self.get_stock_data('AAPL')
            
            if data is not None:
                print(f"✅ API working! Retrieved {len(data)} days of AAPL data")
                print(f"Latest price: ${data['Close'].iloc[-1]:.2f}")
                print(f"Date range: {data.index[0].strftime('%Y-%m-%d')} to {data.index[-1].strftime('%Y-%m-%d')}")
            else:
                print("❌ API test failed")
                
        except Exception as e:
            print(f"❌ API test error: {e}")
    
    def save_data_to_cache(self, symbol, analysis_data):
        """Save Alpha Vantage data to cache similar to our Yahoo Finance cache"""
        cache_dir = "alpha_vantage_cache"
        os.makedirs(cache_dir, exist_ok=True)
        
        # Save raw data
        cache_file = f"{cache_dir}/{symbol}_data.pkl"
        analysis_data['data'].to_pickle(cache_file)
        
        # Save summary
        summary_file = f"{cache_dir}/{symbol}_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(analysis_data['summary'], f, indent=2)
        
        print(f"💾 Data cached to {cache_file}")

def main():
    """Main function to explore Alpha Vantage"""
    print("🚀 Alpha Vantage Explorer")
    print("=" * 40)
    
    explorer = AlphaVantageExplorer()
    
    if not explorer.api_key:
        print("❌ No API key available. Please get one from alphavantage.co")
        return
    
    print("\nOptions:")
    print("1. Test API functionality")
    print("2. Analyze single stock")
    print("3. Compare with Yahoo Finance")
    print("4. Analyze multiple stocks")
    print("5. Test rate limits")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == '1':
        explorer.test_api_limits()
    
    elif choice == '2':
        symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
        if symbol:
            analysis = explorer.create_stock_analysis(symbol)
            if analysis:
                print(f"\n📊 Analysis for {symbol}:")
                for key, value in analysis['summary'].items():
                    print(f"  {key}: {value}")
                
                # Ask to save
                save = input("\nSave to cache? (y/N): ").strip().lower()
                if save == 'y':
                    explorer.save_data_to_cache(symbol, analysis)
    
    elif choice == '3':
        symbol = input("Enter stock symbol (e.g., AAPL): ").strip().upper()
        if symbol:
            explorer.compare_with_yahoo_finance(symbol)
    
    elif choice == '4':
        symbols = input("Enter stock symbols (comma-separated, e.g., AAPL,GOOGL,MSFT): ").strip().upper()
        if symbols:
            symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
            for symbol in symbol_list:
                analysis = explorer.create_stock_analysis(symbol)
                if analysis:
                    print(f"\n📊 {symbol}: ${analysis['summary']['current_price']} | "
                          f"RSI: {analysis['summary']['rsi']} | "
                          f"Trend: {'Bullish' if analysis['summary']['is_bullish'] else 'Bearish' if analysis['summary']['is_bearish'] else 'Neutral'}")
    
    elif choice == '5':
        # Test rate limits by making several requests
        print("Testing rate limits with multiple requests...")
        symbols = ['AAPL', 'GOOGL', 'MSFT']
        for symbol in symbols:
            print(f"\nTesting {symbol}...")
            data = explorer.get_stock_data(symbol)
            if data is not None:
                print(f"✅ {symbol}: ${data['Close'].iloc[-1]:.2f}")
            else:
                print(f"❌ {symbol}: Failed")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
