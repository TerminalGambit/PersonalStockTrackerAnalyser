from stock_simple import StockSimple
import matplotlib.pyplot as plt
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Stock instances
print("Reloading AAPL and NVDA from cache if available...")
aapl = StockSimple("AAPL")
nvda = StockSimple("NVDA")

# Check if data is available
if not aapl.is_valid():
    print("❌ AAPL data not available - skipping AAPL analysis")
    
if not nvda.is_valid():
    print("❌ NVDA data not available - skipping NVDA analysis")

# Only proceed if we have at least one valid stock
if aapl.is_valid() or nvda.is_valid():
    print("\n📊 Stock Information:")
    print("=" * 40)
    
    # Describe both if available
    if aapl.is_valid():
        print("AAPL Information:")
        aapl.describe()
        print()
    
    if nvda.is_valid():
        print("NVDA Information:")
        nvda.describe()
        print()
    
    # Plot indicators for available stocks
    print("📈 Generating Charts:")
    print("=" * 40)
    
    if aapl.is_valid():
        print("Plotting AAPL indicators...")
        aapl.plot_bollinger_bands()
        aapl.plot_macd()
        aapl.plot_rsi()
        aapl.plot_moving_averages()
        aapl.plot_atr()
        aapl.plot_obv()
        aapl.plot_stochastic()
    
    if nvda.is_valid():
        print("Plotting NVDA indicators...")
        nvda.plot_bollinger_bands()
        nvda.plot_macd()
        nvda.plot_rsi()
        nvda.plot_moving_averages()
        nvda.plot_atr()
        nvda.plot_obv()
        nvda.plot_stochastic()
    
    # Compare the two stocks visually if both are available
    if aapl.is_valid() and nvda.is_valid():
        print("Comparing AAPL vs NVDA...")
        aapl.compare_with(nvda)
        
        # Compare indicators
        print("\n📊 Comparison Analysis:")
        print("=" * 40)
        
        # Manual comparison since we don't have the same method
        print("AAPL vs NVDA Analysis:")
        
        if aapl.is_valid():
            aapl_today = aapl.today()
            aapl_growth = ((aapl.history["Close"].iloc[-1] - aapl.history["Close"].iloc[0]) / aapl.history["Close"].iloc[0]) * 100
            aapl_volatility = aapl.history["Daily Return"].std()
            print(f"AAPL Growth: {aapl_growth:.2f}% | Volatility: {aapl_volatility:.4f}")
        
        if nvda.is_valid():
            nvda_today = nvda.today()
            nvda_growth = ((nvda.history["Close"].iloc[-1] - nvda.history["Close"].iloc[0]) / nvda.history["Close"].iloc[0]) * 100
            nvda_volatility = nvda.history["Daily Return"].std()
            print(f"NVDA Growth: {nvda_growth:.2f}% | Volatility: {nvda_volatility:.4f}")
    
    # Check trend heuristics
    print("\n🔍 Trend Analysis:")
    print("=" * 40)
    
    if aapl.is_valid():
        print("AAPL Analysis:")
        print(f"Is AAPL Bullish? {aapl.is_bullish()}")
        print(f"Is AAPL Bearish? {aapl.is_bearish()}")
        
        # Additional technical analysis
        aapl_latest = aapl.today()
        print(f"AAPL Current Price: ${aapl_latest['Close']:.2f}")
        print(f"AAPL 50-Day MA: ${aapl_latest['50MA']:.2f}")
        print(f"AAPL 200-Day MA: ${aapl_latest['200MA']:.2f}")
        print(f"AAPL RSI: {aapl_latest['RSI']:.2f}")
        print()
    
    if nvda.is_valid():
        print("NVDA Analysis:")
        print(f"Is NVDA Bullish? {nvda.is_bullish()}")
        print(f"Is NVDA Bearish? {nvda.is_bearish()}")
        
        # Additional technical analysis
        nvda_latest = nvda.today()
        print(f"NVDA Current Price: ${nvda_latest['Close']:.2f}")
        print(f"NVDA 50-Day MA: ${nvda_latest['50MA']:.2f}")
        print(f"NVDA 200-Day MA: ${nvda_latest['200MA']:.2f}")
        print(f"NVDA RSI: {nvda_latest['RSI']:.2f}")
        print()
    
    # Summary view
    print("📊 Summary:")
    print("=" * 40)
    if aapl.is_valid():
        print("AAPL Summary:")
        aapl.summary()
        print()
    
    if nvda.is_valid():
        print("NVDA Summary:")
        nvda.summary()
        print()
    
    # Latest available data
    print("📅 Latest Data:")
    print("=" * 40)
    if aapl.is_valid():
        print("Today's AAPL Data:")
        print(f"Close: ${aapl.today()['Close']:.2f}")
        print(f"Volume: {aapl.today()['Volume']:,}")
        print(f"High: ${aapl.today()['High']:.2f}")
        print(f"Low: ${aapl.today()['Low']:.2f}")
        print()
    
    if nvda.is_valid():
        print("Today's NVDA Data:")
        print(f"Close: ${nvda.today()['Close']:.2f}")
        print(f"Volume: {nvda.today()['Volume']:,}")
        print(f"High: ${nvda.today()['High']:.2f}")
        print(f"Low: ${nvda.today()['Low']:.2f}")
        print()
    
    # Save snapshots
    print("💾 Saving Snapshots:")
    print("=" * 40)
    if aapl.is_valid():
        aapl.save_snapshot()
    
    if nvda.is_valid():
        nvda.save_snapshot()
    
    print("\n✅ Analysis Complete!")
    print("Charts have been displayed and snapshots saved.")
    print("Note: Stock info may be limited due to API rate limiting.")
    print("Historical data and technical analysis are fully functional.")
    
else:
    print("❌ No stock data available. This could be due to:")
    print("   - No cached data available")
    print("   - API rate limiting from Yahoo Finance")
    print("   - Network connectivity issues")
    print("\nTry running the script again in a few minutes.")
