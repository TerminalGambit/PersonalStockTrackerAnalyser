from portfolio import Portfolio
from visualise_portfolio import PortfolioVisualizer
import os

def run_portfolio_visualization():
    print("📈 Running Portfolio Visualization...\n")

    if os.path.exists("test_portfolio_output.json"):
        portfolio = Portfolio.load_from_json("test_portfolio_output.json")
    else:
        print("⚠️ No portfolio data file found.")
        return

    portfolio.summary()

    visualizer = PortfolioVisualizer(portfolio)
    visualizer.plot_portfolio_value()
    visualizer.plot_individual_stock_values()
    visualizer.plot_allocation_pie()

if __name__ == "__main__":
    run_portfolio_visualization()