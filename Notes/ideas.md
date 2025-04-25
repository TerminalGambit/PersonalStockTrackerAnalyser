**Portfolio System Expansion Ideas**

---

# Financial Features

- **Selling Stocks**  
  Implement `.sell(ticker, shares)` method to sell stocks, update balance, holdings, and transaction history with fee.

- **Realized and Unrealized PnL Tracking**  
  Track both:
  - Realized Profit & Loss (PnL) from sales.
  - Unrealized PnL from current holdings based on latest prices.

- **Dividend Tracking**  
  Simulate passive income from dividends. Optionally allow reinvestment (DRIP).

- **Multiple Currencies Support**  
  Simulate forex conversion if buying international stocks.

- **Brokerage Fee Tiers**  
  Support different broker fee models: flat fee, percentage, or minimum fees.

---

# Strategy and Intelligence

- **Indicator-Aware Strategies**  
  Build automated buy/sell strategies based on indicators:
  - RSI (<30 = buy)
  - MACD crossovers
  - Moving average crossovers (Golden Cross, Death Cross)

- **Backtesting Engine**  
  Given historical data, simulate applying a strategy and measure:
  - Total return
  - Sharpe ratio
  - Max drawdown

- **Risk Management**  
  Add max position size limits and stop-loss triggers (auto-sell after a certain % loss).

---

# Visualization and Reporting

- **Portfolio Value Over Time Graph**  
  Plot total portfolio value progression.

- **Individual Stock Performance**  
  Breakdown per stock: gain, loss, weight in portfolio.

- **Monthly Portfolio Reports**  
  Generate end-of-month snapshots.

- **Benchmark Comparison**  
  Compare returns vs major indices (e.g., SP500).

---

# Data and Storage

- **Better JSON or CSV Export**  
  Save and load portfolio history cleanly.

- **SQLite Database Storage (Advanced)**  
  Persist data in a lightweight local database instead of files.

---

# Code and Architecture Improvements

- **Transaction Class**  
  Model every buy and sell transaction properly.

- **Position Class**  
  Track stock-specific holdings including quantity, cost basis, PnL.

- **Error Handling and Logging**  
  Validate operations like over-selling and provide clear logs.

- **Unit Tests**  
  Create tests to verify critical portfolio behaviors.

---

# Bonus Ideas

- **What If Simulations**  
  Simulate "What if I had invested X at Y date?"

- **Random Daily News Impact Simulator**  
  Model market-moving news to impact prices randomly for realism.

- **Borrowing and Margin Accounts**  
  Simulate leverage by borrowing money to buy more stocks.

- **Tax Simulator**  
  Track capital gains and estimate tax bills annually.

---

# Prioritization Proposal

| Step | Feature                                | Category           |
|:----:|----------------------------------------|--------------------|
| 1    | Sell stocks                            | Core finance       |
| 2    | Track realized/unrealized PnL           | Core finance       |
| 3    | Graph portfolio value over time        | Visualization      |
| 4    | Simulate basic strategies (RSI, MACD)  | Strategy           |
| 5    | Backtest strategies over history       | Intelligence       |
| 6    | Add stop-losses, cash management       | Risk Management    |

