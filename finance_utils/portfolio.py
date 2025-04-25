import json
from datetime import datetime
from stock import Stock
from portfolio_stock import PortfolioStock

class Portfolio:
    def __init__(self, initial_balance=100_000, transaction_fee=15):
        self.balance = initial_balance
        self.transaction_fee = transaction_fee
        self.holdings = {}
        self.transactions = []

    def buy(self, ticker, shares):
        stock = Stock(ticker)
        current_price = stock.history["Close"].iloc[-1]
        total_cost = shares * current_price + self.transaction_fee

        if total_cost > self.balance:
            print("❌ Not enough balance.")
            return False

        self.balance -= total_cost
        if ticker not in self.holdings:
            self.holdings[ticker] = PortfolioStock(ticker)
        self.holdings[ticker].buy(shares, current_price, datetime.now().isoformat())

        self.transactions.append({
            "type": "buy",
            "ticker": ticker,
            "shares": shares,
            "price": current_price,
            "total_cost": total_cost,
            "timestamp": datetime.now().isoformat()
        })

        print(f"✅ Bought {shares} shares of {ticker} at {current_price:.2f}. Remaining balance: €{self.balance:.2f}")
        return True

    def summary(self):
        print(f"📊 Portfolio Summary — Balance: €{self.balance:.2f}")
        for ticker, position in self.holdings.items():
            latest_price = Stock(ticker).history["Close"].iloc[-1]
            current_value = latest_price * position.total_shares
            gain = current_value - position.total_cost
            print(f"{ticker}: {position.total_shares} shares | Avg: €{position.avg_price:.2f} | Now: €{latest_price:.2f} | PnL: €{gain:.2f}")

    def save_to_json(self, filepath='portfolio.json'):
        data = {
            "balance": self.balance,
            "transaction_fee": self.transaction_fee,
            "transactions": self.transactions,
            "holdings": {
                ticker: {
                    "shares": stock.total_shares,
                    "avg_price": stock.avg_price,
                    "history": stock.history
                } for ticker, stock in self.holdings.items()
            }
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Portfolio saved to {filepath}")
