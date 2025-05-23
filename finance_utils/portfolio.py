import json
from datetime import datetime
from stock import Stock
from portfolio_stock import PortfolioStock
from transactions import Transactions


class Portfolio:
    def __init__(self, initial_balance=100_000, transaction_fee=15):
        self.balance = initial_balance
        self.transaction_fee = transaction_fee
        self.holdings = {}
        self.transactions = Transactions()

    def buy(self, ticker, shares, date=None):
        stock = Stock(ticker)
        current_price = stock.history["Close"].iloc[-1]
        total_cost = shares * current_price + self.transaction_fee

        if total_cost > self.balance:
            print("❌ Not enough balance.")
            return False

        self.balance -= total_cost
        if ticker not in self.holdings:
            self.holdings[ticker] = PortfolioStock(ticker)
        buy_date = date or datetime.now().isoformat()
        self.holdings[ticker].buy(
            shares, current_price, buy_date)

        self.transactions.record_buy(
            ticker, shares, current_price, self.transaction_fee, buy_date)

        print(
            f"✅ Bought {shares} shares of {ticker} at {current_price:.2f}. Remaining balance: €{self.balance:.2f}")
        return True

    def sell(self, ticker, shares):
        if ticker not in self.holdings:
            print(f"❌ You don't own any {ticker}.")
            return False

        stock = Stock(ticker)
        current_price = stock.history["Close"].iloc[-1]

        if shares > self.holdings[ticker].total_shares:
            print("❌ Not enough shares to sell.")
            return False

        total_revenue = shares * current_price - self.transaction_fee
        self.balance += total_revenue
        self.holdings[ticker].sell(
            shares, current_price, datetime.now().isoformat())

        self.transactions.record_sell(
            ticker, shares, current_price, self.transaction_fee)

        print(
            f"✅ Sold {shares} shares of {ticker} at {current_price:.2f}. New balance: €{self.balance:.2f}")
        return True

    def summary(self):
        print(f"📊 Portfolio Summary — Balance: €{self.balance:.2f}")
        for ticker, position in self.holdings.items():
            latest_price = Stock(ticker).history["Close"].iloc[-1]
            current_value = position.current_value(latest_price)
            gain = position.unrealized_gain(latest_price)
            print(f"{ticker}: {position.total_shares} shares | Avg: €{position.avg_price:.2f} | Now: €{latest_price:.2f} | PnL: €{gain:.2f}")

    def save_to_json(self, filepath='portfolio.json'):
        data = {
            "balance": self.balance,
            "transaction_fee": self.transaction_fee,
            "transactions": self.transactions.records,
            "holdings": {
                ticker: {
                    "shares": stock.total_shares,
                    "avg_price": stock.avg_price,
                    "history": stock.history if isinstance(stock.history, list) else stock.history.to_dict() if hasattr(stock.history, "to_dict") else stock.history
                } for ticker, stock in self.holdings.items()
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Portfolio saved to {filepath}")

    @classmethod
    def load_from_json(cls, filepath='portfolio.json'):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                if not data or "balance" not in data:
                    raise ValueError("Invalid or empty portfolio data.")
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            print(f"⚠️ Failed to load portfolio: {e}. Starting a new one.")
            return cls()

        portfolio = cls(
            initial_balance=data["balance"],
            transaction_fee=data["transaction_fee"]
        )

        for tx in data.get("transactions", []):
            portfolio.transactions.records.append(tx)

        for ticker, stock_data in data.get("holdings", {}).items():
            ps = PortfolioStock(ticker)
            ps.total_shares = stock_data["shares"]
            ps.total_cost = stock_data["shares"] * stock_data["avg_price"]
            ps.history = stock_data["history"]
            portfolio.holdings[ticker] = ps

        return portfolio
