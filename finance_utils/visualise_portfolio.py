import matplotlib.pyplot as plt
import pandas as pd
from stock import Stock

class PortfolioVisualizer:
    def __init__(self, portfolio):
        self.portfolio = portfolio

    def plot_portfolio_value(self):
        """Plot portfolio total value over time."""
        total_values = []
        dates = pd.date_range(end=pd.Timestamp.today(), periods=180)
        stock_data_cache = {ticker: Stock(ticker).history for ticker in self.portfolio.holdings.keys()}

        for date in dates:
            daily_value = self.portfolio.balance
            for ticker, stock in self.portfolio.holdings.items():
                stock_data = stock_data_cache[ticker]
                if date.strftime('%Y-%m-%d') in stock_data.index:
                    price = stock_data.loc[date.strftime('%Y-%m-%d'), 'Close']
                    daily_value += stock.total_shares * price
            total_values.append(daily_value)

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
        dates = pd.date_range(end=pd.Timestamp.today(), periods=180)
        stock_data_cache = {ticker: Stock(ticker).history for ticker in self.portfolio.holdings.keys()}

        plt.figure(figsize=(12, 8))
        for ticker, stock in self.portfolio.holdings.items():
            prices = []
            stock_data = stock_data_cache[ticker]
            for date in dates:
                if date.strftime('%Y-%m-%d') in stock_data.index:
                    price = stock_data.loc[date.strftime('%Y-%m-%d'), 'Close']
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
        stock_price_cache = {ticker: Stock(ticker).history["Close"].iloc[-1] for ticker in self.portfolio.holdings.keys()}

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