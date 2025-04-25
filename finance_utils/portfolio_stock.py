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

    def current_value(self, latest_price):
        return self.total_shares * latest_price

    def unrealized_gain(self, latest_price):
        return self.current_value(latest_price) - self.total_cost

    def sell(self, shares, price, date):
        if shares > self.total_shares:
            raise ValueError("Not enough shares to sell.")
        self.total_shares -= shares
        self.total_cost -= shares * self.avg_price
        self.history.append({
            "shares": -shares,
            "price": price,
            "date": date
        })

    @property
    def avg_price(self):
        return self.total_cost / self.total_shares if self.total_shares else 0
