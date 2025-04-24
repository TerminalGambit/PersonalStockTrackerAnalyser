from finance_utils import Stock

# Create Stock instances
print("Reloading AAPL and NVDA from cache if available...")
aapl = Stock("AAPL")
nvda = Stock("NVDA")

# Describe both
aapl.describe()
nvda.describe()

# Plot indicators
aapl.plot_bollinger_bands()
nvda.plot_bollinger_bands()

aapl.plot_macd()
nvda.plot_macd()

aapl.plot_rsi()
nvda.plot_rsi()

aapl.plot_moving_averages()
nvda.plot_moving_averages()

aapl.plot_atr()
nvda.plot_atr()

aapl.plot_obv()
nvda.plot_obv()

aapl.plot_stochastic()
nvda.plot_stochastic()

# Compare the two stocks visually
aapl.compare_with(nvda)

# Compare indicators
aapl.compare_indicators(nvda)

# Check trend heuristics
print("\nTrend Heuristics:")
print("Is AAPL Bullish?", aapl.is_bullish())
print("Is AAPL Bearish?", aapl.is_bearish())
print("Is NVDA Bullish?", nvda.is_bullish())
print("Is NVDA Bearish?", nvda.is_bearish())

# Summary view
print("\nSummary:")
aapl.summary()
nvda.summary()

# Latest available data
print("\nToday's AAPL Data:")
print(aapl.today())
print("\nToday's NVDA Data:")
print(nvda.today())

# Save a snapshot
aapl.save_snapshot()
nvda.save_snapshot()

# Save different period of data
aapl.to_csv_custom(period="6mo")
nvda.to_csv_custom(period="6mo")

# Plot candlestick chart (requires mplfinance)
aapl.plot_candlestick()
nvda.plot_candlestick()