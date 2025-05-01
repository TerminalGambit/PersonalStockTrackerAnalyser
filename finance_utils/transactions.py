import json
from datetime import datetime


class Transactions:
    def __init__(self):
        self.records = []

    def record_buy(self, ticker, shares, price, transaction_fee, timestamp=None):
        self.records.append({
            "type": "buy",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "transaction_fee": transaction_fee,
            "timestamp": timestamp or datetime.now().isoformat()
        })

    def record_sell(self, ticker, shares, price, transaction_fee):
        self.records.append({
            "type": "sell",
            "ticker": ticker,
            "shares": shares,
            "price": price,
            "transaction_fee": transaction_fee,
            "timestamp": datetime.now().isoformat()
        })

    def save_to_json(self, filepath='transactions.json'):
        with open(filepath, 'w') as f:
            json.dump(self.records, f, indent=2)
        print(f"💾 Transactions saved to {filepath}")

    def load_from_json(self, filepath='transactions.json'):
        with open(filepath, 'r') as f:
            self.records = json.load(f)
        print(f"📂 Transactions loaded from {filepath}")

    def summary(self):
        print(f"🧾 Transaction History ({len(self.records)} total)")
        for tx in self.records:
            print(f"{tx['timestamp']}: {tx['type'].upper()} {tx['shares']} x {tx['ticker']} at €{tx['price']:.2f} (+fee €{tx['transaction_fee']:.2f})")
