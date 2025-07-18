import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import logging
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

CACHE_DIR = Path("./.stock_cache")
CACHE_DIR.mkdir(exist_ok=True)


def is_cache_valid(filepath, max_age_days=90):
    """Check if cache is valid. Extended to 90 days due to API issues."""
    if not filepath.exists():
        return False
    mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
    return datetime.now() - mod_time < timedelta(days=max_age_days)


class StockSimple:
    """
    A simple and robust Stock class that prioritizes cached data and handles API failures gracefully.
    """
    
    def __init__(self, ticker, period="1y"):
        self.ticker = ticker.upper()
        self.period = period
        self.info = {}
        self.history = pd.DataFrame()
        self._yf = None
        
        # Initialize data
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize stock data with fallback to cached data."""
        logger.info(f"Initializing data for {self.ticker}")
        
        # First, try to load cached data
        self.history = self._load_cached_data()
        
        # If we have cached data, use it
        if not self.history.empty:
            logger.info(f"Using cached data for {self.ticker}")
            self._enrich_data()
            self._try_get_info()
        else:
            logger.warning(f"No cached data found for {self.ticker}")
            self._try_fresh_data()
    
    def _load_cached_data(self):
        """Load cached data if available."""
        cache_file = CACHE_DIR / f"{self.ticker}_{self.period}.csv"
        
        if is_cache_valid(cache_file):
            try:
                logger.info(f"📁 Loading cached data for {self.ticker}")
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)
            except Exception as e:
                logger.error(f"Failed to load cached data for {self.ticker}: {str(e)}")
                return pd.DataFrame()
        else:
            logger.info(f"No valid cached data for {self.ticker}")
            return pd.DataFrame()
    
    def _try_fresh_data(self):
        """Try to fetch fresh data from Yahoo Finance."""
        logger.info(f"Attempting to fetch fresh data for {self.ticker}")
        
        try:
            # Create yfinance ticker
            self._yf = yf.Ticker(self.ticker)
            
            # Try to get historical data with timeout
            df = self._yf.history(period=self.period)
            
            if not df.empty:
                logger.info(f"✅ Successfully fetched fresh data for {self.ticker}")
                self.history = df
                
                # Cache the data
                cache_file = CACHE_DIR / f"{self.ticker}_{self.period}.csv"
                df.to_csv(cache_file)
                
                # Enrich and get info
                self._enrich_data()
                self._try_get_info()
            else:
                logger.warning(f"Empty data returned for {self.ticker}")
                
        except Exception as e:
            logger.error(f"Failed to fetch fresh data for {self.ticker}: {str(e)}")
    
    def _try_get_info(self):
        """Try to get stock info, with fallback to basic info."""
        try:
            if self._yf is None:
                self._yf = yf.Ticker(self.ticker)
            
            # Try to get info
            info = self._yf.info
            if info:
                self.info = info
                logger.info(f"✅ Successfully retrieved info for {self.ticker}")
            else:
                logger.warning(f"No info available for {self.ticker}")
                self._create_basic_info()
                
        except Exception as e:
            logger.error(f"Failed to get info for {self.ticker}: {str(e)}")
            self._create_basic_info()
    
    def _create_basic_info(self):
        """Create basic info from available data."""
        if not self.history.empty:
            latest = self.history.iloc[-1]
            self.info = {
                'symbol': self.ticker,
                'shortName': self.ticker,
                'longName': f"{self.ticker} Inc.",
                'currentPrice': latest['Close'],
                'regularMarketPrice': latest['Close'],
                'regularMarketVolume': latest['Volume'],
                'currency': 'USD'
            }
            logger.info(f"Created basic info for {self.ticker}")
    
    def _enrich_data(self):
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
            
            logger.info(f"Successfully enriched data for {self.ticker}")
            
        except Exception as e:
            logger.error(f"Error enriching data for {self.ticker}: {str(e)}")
    
    def is_valid(self):
        """Check if the stock has valid data."""
        return not self.history.empty
    
    def describe(self):
        """Print company information."""
        if not self.info:
            print(f"📊 {self.ticker} - Limited information available")
            return
        
        print(f"📊 {self.ticker} - {self.info.get('longName', self.info.get('shortName', 'Unknown Company'))}")
        print(f"Industry: {self.info.get('industry', 'N/A')}")
        
        market_cap = self.info.get('marketCap', 'N/A')
        if market_cap != 'N/A' and isinstance(market_cap, (int, float)):
            print(f"Market Cap: ${market_cap:,.0f}")
        else:
            print(f"Market Cap: {market_cap}")
        
        print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
        print(f"Price: ${self.info.get('currentPrice', self.info.get('regularMarketPrice', 'N/A'))}")
        print(f"Website: {self.info.get('website', 'N/A')}")
    
    def summary(self):
        """Print a summary of the stock."""
        if not self.is_valid():
            print(f"❌ No valid data available for {self.ticker}")
            return
        
        print(f"Summary for {self.ticker}")
        
        # Calculate growth and volatility
        start_price = self.history["Close"].iloc[0]
        end_price = self.history["Close"].iloc[-1]
        growth = ((end_price - start_price) / start_price) * 100
        volatility = self.history["Daily Return"].std()
        
        print(f"Period: {self.history.index[0].strftime('%Y-%m-%d')} to {self.history.index[-1].strftime('%Y-%m-%d')}")
        print(f"Growth: {growth:.2f}%")
        print(f"Volatility: {volatility:.4f}")
        print(f"Latest Close: ${end_price:.2f}")
        
        if self.info:
            print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
            market_cap = self.info.get('marketCap', 'N/A')
            if market_cap != 'N/A' and isinstance(market_cap, (int, float)):
                print(f"Market Cap: ${market_cap:,.0f}")
    
    def today(self):
        """Return the latest available data."""
        if self.history.empty:
            return None
        return self.history.iloc[-1]
    
    def plot_moving_averages(self):
        """Plot moving averages."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["Close"], label="Close Price", linewidth=2)
        plt.plot(self.history["50MA"], label="50-Day MA", linestyle="--", alpha=0.7)
        plt.plot(self.history["200MA"], label="200-Day MA", linestyle="--", alpha=0.7)
        plt.title(f"{self.ticker} - Moving Averages")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_rsi(self):
        """Plot RSI."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["RSI"], label="RSI", color="purple")
        plt.axhline(70, color="red", linestyle="--", alpha=0.7, label="Overbought (70)")
        plt.axhline(30, color="green", linestyle="--", alpha=0.7, label="Oversold (30)")
        plt.title(f"{self.ticker} - RSI")
        plt.xlabel("Date")
        plt.ylabel("RSI")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_bollinger_bands(self):
        """Plot Bollinger Bands."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["Close"], label="Close Price", linewidth=2)
        plt.plot(self.history["Upper Band"], label="Upper Band", linestyle="--", color="red", alpha=0.7)
        plt.plot(self.history["Lower Band"], label="Lower Band", linestyle="--", color="green", alpha=0.7)
        plt.fill_between(self.history.index, self.history["Lower Band"], 
                        self.history["Upper Band"], alpha=0.1, color="gray")
        plt.title(f"{self.ticker} - Bollinger Bands")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_macd(self):
        """Plot MACD."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["MACD"], label="MACD", color="blue")
        plt.plot(self.history["Signal"], label="Signal", color="red")
        plt.bar(self.history.index, self.history["Histogram"], 
                label="Histogram", alpha=0.3, color="gray")
        plt.axhline(0, color="black", linewidth=0.5)
        plt.title(f"{self.ticker} - MACD")
        plt.xlabel("Date")
        plt.ylabel("MACD")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_atr(self):
        """Plot ATR."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["ATR"], label="ATR", color="orange")
        plt.title(f"{self.ticker} - Average True Range")
        plt.xlabel("Date")
        plt.ylabel("ATR")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_obv(self):
        """Plot OBV."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["OBV"], label="OBV", color="green")
        plt.title(f"{self.ticker} - On-Balance Volume")
        plt.xlabel("Date")
        plt.ylabel("OBV")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def plot_stochastic(self):
        """Plot Stochastic Oscillator."""
        if self.history.empty:
            print(f"❌ No data available for {self.ticker}")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["%K"], label="%K", color="purple")
        plt.plot(self.history["%D"], label="%D", color="orange")
        plt.axhline(80, color="red", linestyle="--", alpha=0.7, label="Overbought (80)")
        plt.axhline(20, color="green", linestyle="--", alpha=0.7, label="Oversold (20)")
        plt.title(f"{self.ticker} - Stochastic Oscillator")
        plt.xlabel("Date")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def compare_with(self, other_stock):
        """Compare with another stock."""
        if not isinstance(other_stock, StockSimple):
            print("❌ Comparison requires another StockSimple instance")
            return
        
        if self.history.empty or other_stock.history.empty:
            print("❌ Cannot compare - missing data")
            return
        
        plt.figure(figsize=(12, 6))
        plt.plot(self.history["Close"], label=f"{self.ticker}", linewidth=2)
        plt.plot(other_stock.history["Close"], label=f"{other_stock.ticker}", linewidth=2)
        plt.title(f"Comparison: {self.ticker} vs {other_stock.ticker}")
        plt.xlabel("Date")
        plt.ylabel("Price ($)")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()
    
    def save_snapshot(self, filename=None):
        """Save data snapshot."""
        if self.history.empty:
            print(f"❌ No data to save for {self.ticker}")
            return
        
        if filename is None:
            filename = f"{self.ticker}_snapshot.csv"
        
        self.history.to_csv(filename)
        print(f"✅ Snapshot saved to {filename}")
    
    def is_bullish(self):
        """Simple bullish indicator."""
        if self.history.empty:
            return False
        
        latest = self.history.iloc[-1]
        return (latest["Close"] > latest["50MA"] and 
                latest["Close"] > latest["200MA"] and
                latest["RSI"] < 70)
    
    def is_bearish(self):
        """Simple bearish indicator."""
        if self.history.empty:
            return False
        
        latest = self.history.iloc[-1]
        return (latest["Close"] < latest["50MA"] and 
                latest["Close"] < latest["200MA"] and
                latest["RSI"] > 30)
