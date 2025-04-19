# finance_etls.py

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


class Stock:
    def __init__(self, ticker):
        self.ticker = ticker.upper()
        self._yf = yf.Ticker(self.ticker)

        # Core data
        self.info = self._yf.info
        self.history = self._yf.history(period="1y")
        
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
        • self.history               → Access enriched DataFrame
        • self.info                  → Access full Yahoo metadata
        """)