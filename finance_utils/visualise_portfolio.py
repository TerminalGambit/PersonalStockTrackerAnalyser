import matplotlib.pyplot as plt
import pandas as pd
from stock import Stock


class PortfolioVisualizer:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def plot_portfolio_value(self):
        """Plot portfolio total value over time."""
        total_values = []
        # Determine the earliest transaction date
        if not self.portfolio.transactions.records:
            print("⚠️ No transactions found. Cannot plot portfolio value.")
            return
        earliest_date = min(
            pd.to_datetime(tx["timestamp"]).tz_localize("UTC") if pd.to_datetime(tx["timestamp"]).tzinfo is None else pd.to_datetime(tx["timestamp"])
            for tx in self.portfolio.transactions.records
        )
        if earliest_date.tzinfo is None:
            earliest_date = earliest_date.tz_localize("UTC")
        dates = pd.date_range(start=earliest_date, end=pd.Timestamp.now(tz="UTC"))
        stock_data_cache = {}
        for ticker in self.portfolio.holdings.keys():
            stock_data = Stock(ticker).history
            stock_data.index = pd.to_datetime(stock_data.index, utc=True)
            stock_data_cache[ticker] = stock_data

        for date in dates:
            date = pd.to_datetime(date).tz_localize("UTC") if date.tzinfo is None else date
            daily_value = 0
            for ticker, stock in self.portfolio.holdings.items():
                stock_data = stock_data_cache[ticker]
                # Skip if no shares bought yet or no data for this date
                available_dates = stock_data.index[stock_data.index <= date]
                if not available_dates.empty:
                    last_available_date = available_dates[-1]
                    price = stock_data.loc[last_available_date, 'Close']
                    daily_value += stock.total_shares * price
            total_values.append(daily_value + self.portfolio.balance)

        plt.figure(figsize=(10, 6))
        plt.plot(dates, total_values, label="Portfolio Value")
        plt.title("Portfolio Total Value Over Time")
        plt.xlabel("Date")
        plt.ylabel("Value (€)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def plot_individual_stock_values(self):
        """Plot individual stock values over time."""
        # Determine the earliest transaction date
        if not self.portfolio.transactions.records:
            print("⚠️ No transactions found. Cannot plot individual stock values.")
            return
        earliest_date = min(
            pd.to_datetime(tx["timestamp"]).tz_localize("UTC") if pd.to_datetime(tx["timestamp"]).tzinfo is None else pd.to_datetime(tx["timestamp"])
            for tx in self.portfolio.transactions.records
        )
        if earliest_date.tzinfo is None:
            earliest_date = earliest_date.tz_localize("UTC")
        dates = pd.date_range(start=earliest_date, end=pd.Timestamp.now(tz="UTC"))
        stock_data_cache = {}
        for ticker in self.portfolio.holdings.keys():
            stock_data = Stock(ticker).history
            stock_data.index = pd.to_datetime(stock_data.index, utc=True)
            stock_data_cache[ticker] = stock_data

        plt.figure(figsize=(12, 8))
        for ticker, stock in self.portfolio.holdings.items():
            prices = []
            stock_data = stock_data_cache[ticker]
            for date in dates:
                date = pd.to_datetime(date).tz_localize("UTC") if date.tzinfo is None else date
                available_dates = stock_data.index[stock_data.index <= date]
                if not available_dates.empty:
                    last_available_date = available_dates[-1]
                    price = stock_data.loc[last_available_date, 'Close']
                    prices.append(price * stock.total_shares)
                else:
                    prices.append(None)
            plt.plot(dates, prices, label=f"{ticker}")

        plt.title("Individual Stock Values Over Time")
        plt.xlabel("Date")
        plt.ylabel("Value (€)")
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()

    def plot_allocation_pie(self):
        """Plot current portfolio allocation as a pie chart."""
        labels = []
        sizes = []
        stock_price_cache = {ticker: Stock(
            ticker).history["Close"].iloc[-1] for ticker in self.portfolio.holdings.keys()}

        for ticker, stock in self.portfolio.holdings.items():
            latest_price = stock_price_cache[ticker]
            value = stock.total_shares * latest_price
            labels.append(ticker)
            sizes.append(value)

        plt.figure(figsize=(8, 8))
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
        plt.title("Portfolio Allocation")
        plt.tight_layout()
        plt.show()
