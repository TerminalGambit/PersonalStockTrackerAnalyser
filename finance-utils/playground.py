from finance_utils import Stock

# Create Stock instances
aapl = Stock("AAPL")
nvda = Stock("NVDA")

# Describe both
aapl.describe()
nvda.describe()

# # Plot indicators
# aapl.plot_bollinger_bands()
# nvda.plot_bollinger_bands()

# aapl.plot_macd()
# nvda.plot_macd()

# aapl.plot_rsi()
# nvda.plot_rsi()

# aapl.plot_moving_averages()
# nvda.plot_moving_averages()

# Compare the two stocks
aapl.compare_with(nvda)
aapl.compare_indicators(nvda)

# Check trend heuristics
print("Is AAPL Bullish?", aapl.is_bullish())
print("Is AAPL Bearish?", aapl.is_bearish())
print("Is NVDA Bullish?", nvda.is_bullish())
print("Is NVDA Bearish?", nvda.is_bearish())

# Summary view
aapl.summary()
nvda.summary()

# Latest available data
print("AAPL Today:")
print(aapl.today())
print("NVDA Today:")
print(nvda.today())

# # Save a snapshot
# aapl.save_snapshot()
# nvda.save_snapshot()

# # Save different period of data
# aapl.to_csv_custom(period="6mo")
# nvda.to_csv_custom(period="6mo")

# aapl.volatility