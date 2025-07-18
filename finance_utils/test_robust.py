#!/usr/bin/env python3
"""
Simple test script to verify the robust Yahoo Finance implementation.
This script tests the new robust implementation with proper error handling.
"""

from stock_robust import StockRobust
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_single_stock(symbol: str):
    """Test a single stock symbol."""
    print(f"\n🧪 Testing {symbol}...")
    print("-" * 40)
    
    try:
        # Create stock instance
        stock = StockRobust(symbol)
        
        # Check if data loaded successfully
        if stock.is_valid():
            print(f"✅ {symbol} data loaded successfully")
            
            # Show basic info
            stock.describe()
            
            # Show today's data
            today_data = stock.today()
            if today_data is not None:
                print(f"Latest Close: ${today_data['Close']:.2f}")
                print(f"Latest Volume: {today_data['Volume']:,}")
            
            # Show summary
            print(f"\n📊 {symbol} Summary:")
            stock.summary()
            
            return True
        else:
            print(f"❌ {symbol} data failed to load")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {symbol}: {str(e)}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Robust Yahoo Finance Implementation")
    print("=" * 50)
    
    # Test individual stocks
    symbols = ["AAPL", "NVDA", "GOOGL"]
    results = {}
    
    for symbol in symbols:
        results[symbol] = test_single_stock(symbol)
        time.sleep(1)  # Be respectful to the API
    
    # Show test results
    print("\n" + "=" * 50)
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    successful = 0
    for symbol, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{symbol}: {status}")
        if success:
            successful += 1
    
    print(f"\nOverall: {successful}/{len(symbols)} stocks loaded successfully")
    
    if successful == 0:
        print("\n⚠️  No stocks loaded successfully.")
        print("This might be due to:")
        print("   - Rate limiting from Yahoo Finance")
        print("   - Network connectivity issues")
        print("   - API changes at Yahoo Finance")
        print("   - Missing dependencies")
        print("\nTry running the script again in a few minutes.")
    elif successful < len(symbols):
        print("\n⚠️  Some stocks failed to load.")
        print("This is likely due to rate limiting.")
        print("The robust implementation will cache successful data.")
        print("Try running the script again to load the remaining stocks.")
    else:
        print("\n🎉 All stocks loaded successfully!")
        print("The robust implementation is working correctly.")

if __name__ == "__main__":
    main()
