from stock_robust import StockRobust
import time
import logging

# Set up logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main function to test the robust stock implementation."""
    print("🚀 Testing robust stock implementation...")
    print("=" * 50)
    
    # Create Stock instances with error handling
    print("Creating AAPL stock instance...")
    aapl = StockRobust("AAPL")
    
    # Add a small delay to be respectful to the API
    time.sleep(2)
    
    print("Creating NVDA stock instance...")
    nvda = StockRobust("NVDA")
    
    print("=" * 50)
    print("📊 Stock Information:")
    print("=" * 50)
    
    # Check if stocks are valid before proceeding
    if aapl.is_valid():
        print("✅ AAPL data loaded successfully")
        aapl.describe()
        print()
    else:
        print("❌ AAPL data failed to load")
        print("This could be due to rate limiting or API issues.")
        print("The system will continue with available data.")
        print()
    
    if nvda.is_valid():
        print("✅ NVDA data loaded successfully")
        nvda.describe()
        print()
    else:
        print("❌ NVDA data failed to load")
        print("This could be due to rate limiting or API issues.")
        print("The system will continue with available data.")
        print()
    
    # Try plotting if we have data
    print("=" * 50)
    print("📈 Generating Charts (if data is available):")
    print("=" * 50)
    
    if aapl.is_valid():
        print("Plotting AAPL indicators...")
        try:
            aapl.plot_moving_averages()
            aapl.plot_rsi()
            aapl.plot_bollinger_bands()
            aapl.plot_macd()
        except Exception as e:
            logger.error(f"Error plotting AAPL charts: {str(e)}")
    
    if nvda.is_valid():
        print("Plotting NVDA indicators...")
        try:
            nvda.plot_moving_averages()
            nvda.plot_rsi()
            nvda.plot_bollinger_bands()
            nvda.plot_macd()
        except Exception as e:
            logger.error(f"Error plotting NVDA charts: {str(e)}")
    
    # Compare stocks if both are valid
    if aapl.is_valid() and nvda.is_valid():
        print("Comparing AAPL vs NVDA...")
        try:
            aapl.compare_with(nvda)
        except Exception as e:
            logger.error(f"Error comparing stocks: {str(e)}")
    
    # Print summaries
    print("=" * 50)
    print("📊 Summary Reports:")
    print("=" * 50)
    
    if aapl.is_valid():
        print("AAPL Summary:")
        aapl.summary()
        print()
    
    if nvda.is_valid():
        print("NVDA Summary:")
        nvda.summary()
        print()
    
    # Save snapshots if data is available
    print("=" * 50)
    print("💾 Saving Snapshots:")
    print("=" * 50)
    
    if aapl.is_valid():
        aapl.save_snapshot()
    
    if nvda.is_valid():
        nvda.save_snapshot()
    
    print("=" * 50)
    print("✅ Script completed successfully!")
    print("If you encountered rate limiting issues, try running the script again in a few minutes.")
    print("The robust implementation includes retry logic and will cache successful data.")

if __name__ == "__main__":
    main()
