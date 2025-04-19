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

    def describe(self):
        print(f"📊 {self.ticker} - {self.info.get('longName', 'Unknown Company')}")
        print(f"Industry: {self.info.get('industry', 'N/A')}")
        print(f"Market Cap: {self.info.get('marketCap', 'N/A')}")
        print(f"P/E Ratio: {self.info.get('trailingPE', 'N/A')}")
        print(f"Price: {self.info.get('currentPrice', 'N/A')} USD")
        print(f"Website: {self.info.get('website', 'N/A')}")
    
    def plot_bollinger_bands(self):
        df = self.history.copy()
        df["20MA"] = df["Close"].rolling(window=20).mean()
        df["20STD"] = df["Close"].rolling(window=20).std()
        df["Upper Band"] = df["20MA"] + 2 * df["20STD"]
        df["Lower Band"] = df["20MA"] - 2 * df["20STD"]

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

    def help(self):
        print(f"""
        🧰 Stock Class Help:
        ────────────────────
        • .describe()                → Print company info & metrics
        • .plot_bollinger_bands()   → Plot Bollinger Bands chart
        • self.history              → Access enriched DataFrame
        • self.info                 → Access full Yahoo metadata
        
        Upcoming Ideas:
        • .plot_macd()
        • .plot_rsi()
        • .compare_with(other_stock)
        """)