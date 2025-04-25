class PortfolioStock:
    def __init__(self, ticker):
        self.ticker = ticker
        self.total_shares = 0
        self.total_cost = 0
        self.history = []

    def buy(self, shares, price, date):
        self.total_cost += shares * price
        self.total_shares += shares
        self.history.append({
            "shares": shares,
            "price": price,
            "date": date
        })

    @property
    def avg_price(self):
        return self.total_cost / self.total_shares if self.total_shares else 0
