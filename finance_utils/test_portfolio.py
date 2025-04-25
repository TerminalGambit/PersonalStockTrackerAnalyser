from portfolio import Portfolio
from visualise_portfolio import PortfolioVisualizer


def run_portfolio_playground():
    print("📈 Running Portfolio Playground...\n")

    # Initialize a test portfolio with €100,000
    portfolio = Portfolio(initial_balance=100_000, transaction_fee=15)

    # Simulate buying shares
    portfolio.buy("AAPL", 10)
    portfolio.buy("NVDA", 5)

    # Print summary of holdings
    portfolio.summary()

    # Save the portfolio state
    portfolio.save_to_json("test_portfolio_output.json")

    # Visualize the portfolio
    visualizer = PortfolioVisualizer(portfolio)
    visualizer.plot_portfolio_value()
    visualizer.plot_individual_stock_values()
    visualizer.plot_allocation_pie()


if __name__ == "__main__":
    run_portfolio_playground()
