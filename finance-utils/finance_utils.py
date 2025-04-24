import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path
from datetime import datetime, timedelta

CACHE_DIR = Path("./.stock_cache")
CACHE_DIR.mkdir(exist_ok=True)

def is_cache_valid(filepath, max_age_hours=12):
    if not filepath.exists():
        return False
    mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
    return datetime.now() - mod_time < timedelta(hours=max_age_hours)

class Stock:
    def __init__(self, ticker, period="1y"):
        self.ticker = ticker.upper()
        self.period = period
        self._yf = yf.Ticker(self.ticker)

        # Core data
        self.info = self._yf.info
        self.history = self._load_cached_history(period=period)
        
        # Enrich the DataFrame with standard columns
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

    def _load_cached_history(self, period="1y", refresh=False):
        cache_file = CACHE_DIR / f"{self.ticker}_{period}.csv"

        if not refresh and is_cache_valid(cache_file):
            print(f"📁 Loading cached data for {self.ticker}")
            return pd.read_csv(cache_file, index_col=0, parse_dates=True)

        print(f"🌐 Fetching fresh data for {self.ticker}")
        df = self._yf.history(period=period)
        df.to_csv(cache_file)
        return df

    def describe(self):
        print(f"📊 {self.ticker} - {self.info.get('longName', 'Unknown Company')}")
        print(f"Industry: {self.info.get('industry', 'N/A')}")
        print(f"Market Cap: {self.info.get('marketCap', 'N/A')}")
        print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
        print(f"Price: {self.info.get('currentPrice', 'N/A')} USD")
        print(f"Website: {self.info.get('website', 'N/A')}")
    
    def plot_bollinger_bands(self):
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

    def compare_with(self, other_stock):
        if not isinstance(other_stock, Stock):
            print("Comparison requires another Stock instance.")
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
        if filename is None:
            filename = f"{self.ticker}_snapshot.csv"
        self.history.to_csv(filename)
        print(f"Snapshot saved to {filename}")

    def help(self):
        print(f"""
        🧰 Stock Class Help:
        ────────────────────
        • .describe()                → Print company info & metrics
        • .plot_bollinger_bands()    → Plot Bollinger Bands chart
        • .plot_macd()               → Plot MACD indicator
        • .plot_rsi()                → Plot RSI indicator
        • .plot_moving_averages()    → Plot 50 and 200-day moving averages
        • .compare_with(other)       → Compare with another Stock instance
        • .save_snapshot()           → Save historical data to CSV
        • .today()                   → Return the latest available row of historical data
        • .to_csv_custom(period)     → Save a specific period of data to CSV
        • .get_growth()              → Calculate percentage growth over the dataset
        • .volatility()              → Compute volatility as std of daily returns
        • .summary()                 → Print a quick summary of key stats
        • .plot_candlestick()        → Plot a candlestick chart (requires mplfinance)
        • .compare_indicators(other) → Compare growth and volatility with another stock
        • .is_bullish()              → Return True if price is above both MAs
        • .is_bearish()              → Return True if price is below both MAs
        • self.history               → Access enriched DataFrame
        • self.info                  → Access full Yahoo metadata
        """)

    def today(self):
        """Return the latest available row of stock data."""
        return self.history.iloc[-1]

    def to_csv_custom(self, period='1y', filename=None):
        temp_df = self._yf.history(period=period)
        if filename is None:
            filename = f"{self.ticker}_{period}_data.csv"
        temp_df.to_csv(filename)
        print(f"Saved {period} historical data to {filename}")

    def get_growth(self):
        """Calculate percentage growth from the first to the last day in the dataset."""
        start_price = self.history["Close"].iloc[0]
        end_price = self.history["Close"].iloc[-1]
        return ((end_price - start_price) / start_price) * 100

    def volatility(self):
        """Return standard deviation of daily returns."""
        return self.history["Daily Return"].std()

    def summary(self):
        """Print a brief summary of key statistics."""
        print(f"Summary for {self.ticker}")
        print(f"Growth: {self.get_growth():.2f}%")
        print(f"Volatility: {self.volatility():.4f}")
        print(f"Latest Close: {self.history['Close'].iloc[-1]:.2f} USD")
        print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
        print(f"Market Cap: {self.info.get('marketCap', 'N/A')}")

    def plot_candlestick(self):
        """Plot candlestick chart using mplfinance."""
        try:
            import mplfinance as mpf
        except ImportError:
            print("Please install mplfinance with `pip install mplfinance` to use this method.")
            return
        df = self._yf.history(period="3mo")
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        mpf.plot(df, type="candle", volume=True, title=f"{self.ticker} Candlestick Chart")

    def compare_indicators(self, other_stock):
        if not isinstance(other_stock, Stock):
            print("Comparison requires another Stock instance.")
            return

        print(f"Comparing {self.ticker} and {other_stock.ticker}")
        print(f"{self.ticker} Growth: {self.get_growth():.2f}% | Volatility: {self.volatility():.4f}")
        print(f"{other_stock.ticker} Growth: {other_stock.get_growth():.2f}% | Volatility: {other_stock.volatility():.4f}")

    def is_bullish(self):
        """Simple heuristic: bullish if price is above both 50MA and 200MA."""
        latest = self.history.iloc[-1]
        return latest["Close"] > latest["50MA"] and latest["Close"] > latest["200MA"]

    def is_bearish(self):
        """Simple heuristic: bearish if price is below both 50MA and 200MA."""
        latest = self.history.iloc[-1]
        return latest["Close"] < latest["50MA"] and latest["Close"] < latest["200MA"]