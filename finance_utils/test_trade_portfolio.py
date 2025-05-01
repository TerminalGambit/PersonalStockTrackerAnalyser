from portfolio import Portfolio

def run_portfolio_trade_sim():
    print("🎯 Running Portfolio Trade Simulation...\n")
    portfolio = Portfolio(initial_balance=10_000, transaction_fee=15)
    portfolio.buy("AAPL", 20, date="2024-01-01T10:00:00")
    portfolio.buy("NVDA", 10, date="2024-01-01T14:30:00")
    portfolio.save_to_json("test_portfolio_output.json")

if __name__ == "__main__":
    run_portfolio_trade_sim()