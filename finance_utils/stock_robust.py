import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging
from yahoo_finance_client import yahoo_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = Path("./.stock_cache")
CACHE_DIR.mkdir(exist_ok=True)


def is_cache_valid(filepath, max_age_hours=12):
    if not filepath.exists():
        return False
    mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
    return datetime.now() - mod_time < timedelta(hours=max_age_hours)


class StockRobust:
    """
    A robust Stock class that handles Yahoo Finance API errors gracefully
    and implements proper rate limiting and error handling.
    """
    
    def __init__(self, ticker, period="1y", use_fallback=True):
        self.ticker = ticker.upper()
        self.period = period
        self.use_fallback = use_fallback
        self._yf = None
        self.info = {}
        self.history = pd.DataFrame()
        
        # Initialize with error handling
        self._initialize_stock_data()
    
    def _initialize_stock_data(self):
        """Initialize stock data with robust error handling."""
        try:
            # First, try to get basic info using our robust client
            logger.info(f"Initializing data for {self.ticker}")
            
            # Get quote summary using our robust client
            quote_summary = yahoo_client.get_quote_summary(self.ticker)
            if quote_summary and 'quoteSummary' in quote_summary:
                self._extract_info_from_quote_summary(quote_summary)
            
            # Load historical data
            self.history = self._load_cached_history_robust(period=self.period)
            
            # Only enrich if we have valid historical data
            if not self.history.empty:
                self._enrich_historical_data()
            else:
                logger.warning(f"No historical data available for {self.ticker}")
                
        except Exception as e:
            logger.error(f"Error initializing {self.ticker}: {str(e)}")
            
            # If robust client fails, try fallback to yfinance
            if self.use_fallback:
                logger.info(f"Falling back to yfinance for {self.ticker}")
                self._fallback_to_yfinance()
    
    def _extract_info_from_quote_summary(self, quote_summary):
        """Extract info from quote summary response."""
        try:
            result = quote_summary['quoteSummary']['result'][0]
            
            # Extract various data modules
            if 'assetProfile' in result:
                profile = result['assetProfile']
                self.info.update({
                    'longName': profile.get('longBusinessSummary', ''),
                    'industry': profile.get('industry', ''),
                    'sector': profile.get('sector', ''),
                    'website': profile.get('website', ''),
                    'fullTimeEmployees': profile.get('fullTimeEmployees', 0)
                })
            
            if 'summaryDetail' in result:
                summary = result['summaryDetail']
                self.info.update({
                    'marketCap': summary.get('marketCap', {}).get('raw', 0),
                    'trailingPE': summary.get('trailingPE', {}).get('raw', 0),
                    'forwardPE': summary.get('forwardPE', {}).get('raw', 0),
                    'dividendYield': summary.get('dividendYield', {}).get('raw', 0),
                    'beta': summary.get('beta', {}).get('raw', 0)
                })
            
            if 'financialData' in result:
                financial = result['financialData']
                self.info.update({
                    'currentPrice': financial.get('currentPrice', {}).get('raw', 0),
                    'targetMeanPrice': financial.get('targetMeanPrice', {}).get('raw', 0),
                    'recommendationMean': financial.get('recommendationMean', {}).get('raw', 0),
                    'totalCash': financial.get('totalCash', {}).get('raw', 0),
                    'totalDebt': financial.get('totalDebt', {}).get('raw', 0),
                    'totalRevenue': financial.get('totalRevenue', {}).get('raw', 0),
                    'returnOnAssets': financial.get('returnOnAssets', {}).get('raw', 0),
                    'returnOnEquity': financial.get('returnOnEquity', {}).get('raw', 0)
                })
                
        except Exception as e:
            logger.error(f"Error extracting info from quote summary: {str(e)}")
    
    def _fallback_to_yfinance(self):
        """Fallback to using yfinance directly."""
        try:
            logger.info(f"Using yfinance fallback for {self.ticker}")
            self._yf = yf.Ticker(self.ticker)
            
            # Try to get info with timeout
            try:
                self.info = self._yf.info or {}
            except Exception as e:
                logger.warning(f"Could not get info for {self.ticker}: {str(e)}")
                self.info = {}
            
            # Get historical data
            self.history = self._load_cached_history(period=self.period)
            
            # Enrich if we have data
            if not self.history.empty:
                self._enrich_historical_data()
                
        except Exception as e:
            logger.error(f"Fallback to yfinance failed for {self.ticker}: {str(e)}")
            self.info = {}
            self.history = pd.DataFrame()
    
    def _load_cached_history_robust(self, period="1y", refresh=False):
        """Load historical data with robust error handling."""
        cache_file = CACHE_DIR / f"{self.ticker}_{period}.csv"
        
        if not refresh and is_cache_valid(cache_file):
            logger.info(f"📁 Loading cached data for {self.ticker}")
            try:
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)
            except Exception as e:
                logger.warning(f"Failed to load cache for {self.ticker}: {str(e)}")
        
        logger.info(f"🌐 Fetching fresh data for {self.ticker}")
        
        # Try using yfinance with retry logic
        for attempt in range(3):
            try:
                if not self._yf:
                    self._yf = yf.Ticker(self.ticker)
                
                # Add delay between attempts
                if attempt > 0:
                    delay = 2 ** attempt
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                
                df = self._yf.history(period=period)
                
                if not df.empty:
                    df.to_csv(cache_file)
                    return df
                else:
                    logger.warning(f"Empty data returned for {self.ticker}")
                    
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed for {self.ticker}: {str(e)}")
                if attempt == 2:  # Last attempt
                    logger.error(f"All attempts failed for {self.ticker}")
                    return pd.DataFrame()
        
        return pd.DataFrame()
    
    def _load_cached_history(self, period="1y", refresh=False):
        """Original cached history loading method."""
        cache_file = CACHE_DIR / f"{self.ticker}_{period}.csv"
        
        if not refresh and is_cache_valid(cache_file):
            logger.info(f"📁 Loading cached data for {self.ticker}")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        
        logger.info(f"🌐 Fetching fresh data for {self.ticker}")
        try:
            df = self._yf.history(period=period)
            if not df.empty:
                df.to_csv(cache_file)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch data for {self.ticker}: {str(e)}")
            return pd.DataFrame()
    
    def _enrich_historical_data(self):
        """Enrich historical data with technical indicators."""
        if self.history.empty:
            return
            
        try:
            # Basic indicators
            self.history["Daily Return"] = self.history["Close"].pct_change()
            self.history["50MA"] = self.history["Close"].rolling(window=50).mean()
            self.history["200MA"] = self.history["Close"].rolling(window=200).mean()
            
            # MACD components
            self.history["EMA12"] = self.history["Close"].ewm(span=12, adjust=False).mean()
            self.history["EMA26"] = self.history["Close"].ewm(span=26, adjust=False).mean()
            self.history["MACD"] = self.history["EMA12"] - self.history["EMA26"]
            self.history["Signal"] = self.history["MACD"].ewm(span=9, adjust=False).mean()
            self.history["Histogram"] = self.history["MACD"] - self.history["Signal"]
            
            # RSI components
            delta = self.history["Close"].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=14).mean()
            avg_loss = loss.rolling(window=14).mean()
            rs = avg_gain / avg_loss
            self.history["RSI"] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            self.history["20MA"] = self.history["Close"].rolling(window=20).mean()
            self.history["20STD"] = self.history["Close"].rolling(window=20).std()
            self.history["Upper Band"] = self.history["20MA"] + 2 * self.history["20STD"]
            self.history["Lower Band"] = self.history["20MA"] - 2 * self.history["20STD"]
            
            # ATR (Average True Range)
            self.history["H-L"] = self.history["High"] - self.history["Low"]
            self.history["H-PC"] = abs(self.history["High"] - self.history["Close"].shift(1))
            self.history["L-PC"] = abs(self.history["Low"] - self.history["Close"].shift(1))
            self.history["TR"] = self.history[["H-L", "H-PC", "L-PC"]].max(axis=1)
            self.history["ATR"] = self.history["TR"].rolling(window=14).mean()
            
            # OBV (On-Balance Volume)
            direction = self.history["Close"].diff().apply(
                lambda x: 1 if x > 0 else (-1 if x < 0 else 0))
            self.history["OBV"] = (direction * self.history["Volume"]).fillna(0).cumsum()
            
            # Stochastic Oscillator
            low_min = self.history["Low"].rolling(window=14).min()
            high_max = self.history["High"].rolling(window=14).max()
            self.history["%K"] = 100 * (self.history["Close"] - low_min) / (high_max - low_min)
            self.history["%D"] = self.history["%K"].rolling(window=3).mean()
            
        except Exception as e:
            logger.error(f"Error enriching historical data for {self.ticker}: {str(e)}")
    
    def describe(self):
        """Print company information."""
        if not self.info:
            logger.warning(f"No info available for {self.ticker}")
            return
            
        print(f"📊 {self.ticker} - {self.info.get('longName', 'Unknown Company')}")
        print(f"Industry: {self.info.get('industry', 'N/A')}")
        print(f"Market Cap: {self.info.get('marketCap', 'N/A'):,}" if self.info.get('marketCap') else "Market Cap: N/A")
        print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
        print(f"Price: {self.info.get('currentPrice', 'N/A')} USD")
        print(f"Website: {self.info.get('website', 'N/A')}")
    
    def is_valid(self):
        """Check if the stock data is valid."""
        return not self.history.empty and bool(self.info)
    
    def plot_bollinger_bands(self):
        """Plot Bollinger Bands."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        
        plt.figure(figsize=(14, 6))
        plt.plot(df["Close"], label="Close Price")
        plt.plot(df["Upper Band"], label="Upper Band", linestyle="--", color="red")
        plt.plot(df["Lower Band"], label="Lower Band", linestyle="--", color="green")
        plt.fill_between(df.index, df["Lower Band"], df["Upper Band"], color="gray", alpha=0.1)
        plt.title(f"{self.ticker} - Bollinger Bands")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_macd(self):
        """Plot MACD indicator."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        
        plt.figure(figsize=(14, 6))
        plt.plot(df["MACD"], label="MACD", color="blue", linewidth=1.5)
        plt.plot(df["Signal"], label="Signal Line", color="orange", linewidth=1.5)
        plt.bar(df.index, df["Histogram"], label="Histogram", color="gray", alpha=0.5)
        plt.axhline(0, color="black", linewidth=1)
        plt.title(f"{self.ticker} - MACD Indicator")
        plt.xlabel("Date")
        plt.ylabel("MACD Value")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_rsi(self):
        """Plot RSI indicator."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        
        plt.figure(figsize=(14, 6))
        plt.plot(df["RSI"], label="RSI", color="purple")
        plt.axhline(70, color="red", linestyle="--", label="Overbought (70)")
        plt.axhline(30, color="green", linestyle="--", label="Oversold (30)")
        plt.title(f"{self.ticker} - RSI")
        plt.xlabel("Date")
        plt.ylabel("RSI Value")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_moving_averages(self):
        """Plot moving averages."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        
        plt.figure(figsize=(14, 6))
        plt.plot(df["Close"], label="Close Price", linewidth=2)
        plt.plot(df["50MA"], label="50-Day MA", linestyle="--")
        plt.plot(df["200MA"], label="200-Day MA", linestyle="--")
        plt.title(f"{self.ticker} - Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_atr(self):
        """Plot Average True Range."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        plt.figure(figsize=(14, 6))
        plt.plot(df["ATR"], label="ATR (14-day)", color="blue")
        plt.title(f"{self.ticker} - Average True Range (ATR)")
        plt.xlabel("Date")
        plt.ylabel("ATR")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_obv(self):
        """Plot On-Balance Volume."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        plt.figure(figsize=(14, 6))
        plt.plot(df["OBV"], label="On-Balance Volume (OBV)", color="green")
        plt.title(f"{self.ticker} - On-Balance Volume (OBV)")
        plt.xlabel("Date")
        plt.ylabel("OBV")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def plot_stochastic(self):
        """Plot Stochastic Oscillator."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return
            
        df = self.history.copy()
        plt.figure(figsize=(14, 6))
        plt.plot(df["%K"], label="%K", color="purple")
        plt.plot(df["%D"], label="%D", color="orange")
        plt.axhline(80, color="red", linestyle="--", label="Overbought (80)")
        plt.axhline(20, color="green", linestyle="--", label="Oversold (20)")
        plt.title(f"{self.ticker} - Stochastic Oscillator")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def summary(self):
        """Print a summary of the stock."""
        if not self.is_valid():
            logger.warning(f"No valid data available for {self.ticker}")
            return
            
        print(f"Summary for {self.ticker}")
        
        if not self.history.empty:
            start_price = self.history["Close"].iloc[0]
            end_price = self.history["Close"].iloc[-1]
            growth = ((end_price - start_price) / start_price) * 100
            volatility = self.history["Daily Return"].std()
            
            print(f"Growth: {growth:.2f}%")
            print(f"Volatility: {volatility:.4f}")
            print(f"Latest Close: {end_price:.2f} USD")
        
        if self.info:
            print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
            print(f"Market Cap: {self.info.get('marketCap', 'N/A'):,}" if self.info.get('marketCap') else "Market Cap: N/A")
    
    def today(self):
        """Return the latest available row of stock data."""
        if self.history.empty:
            logger.warning(f"No data available for {self.ticker}")
            return None
        return self.history.iloc[-1]
    
    def compare_with(self, other_stock):
        """Compare with another stock."""
        if not isinstance(other_stock, StockRobust):
            print("Comparison requires another StockRobust instance.")
            return
        
        if self.history.empty or other_stock.history.empty:
            print("Cannot compare - one or both stocks have no data.")
            return
            
        plt.figure(figsize=(14, 6))
        plt.plot(self.history["Close"], label=f"{self.ticker} Close", linewidth=2)
        plt.plot(other_stock.history["Close"], label=f"{other_stock.ticker} Close", linewidth=2)
        plt.title(f"Comparison: {self.ticker} vs {other_stock.ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        plt.show()
    
    def save_snapshot(self, filename=None):
        """Save snapshot to CSV."""
        if self.history.empty:
            logger.warning(f"No data to save for {self.ticker}")
            return
            
        if filename is None:
            filename = f"{self.ticker}_snapshot.csv"
        self.history.to_csv(filename)
        print(f"Snapshot saved to {filename}")
