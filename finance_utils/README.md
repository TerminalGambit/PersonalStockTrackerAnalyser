# Robust Yahoo Finance Stock Analyzer

## Overview
This project provides a robust solution for analyzing stock data from Yahoo Finance, handling the common issues of rate limiting, API errors, and authentication failures that plague many Yahoo Finance implementations.

## The Problem
Yahoo Finance's API has several challenges:
- **Rate Limiting**: 429 "Too Many Requests" errors
- **Invalid Crumb**: Authentication token expiration
- **JSON Decode Errors**: Malformed responses
- **API Instability**: Intermittent service disruptions

## The Solution
This implementation provides multiple layers of robustness:

### 1. **Intelligent Caching** (`stock_simple.py`)
- Automatically caches stock data locally
- Uses cached data when fresh data is unavailable
- Configurable cache expiration (default: 90 days)
- Graceful fallback to cached data during API outages

### 2. **Advanced Yahoo Finance Client** (`yahoo_finance_client.py`)
- Implements proper crumb/cookie authentication
- Automatic retry logic with exponential backoff
- Rate limit detection and handling
- Session management for authentication tokens

### 3. **Error-Resilient Stock Class** (`stock_robust.py`)
- Multiple fallback strategies
- Comprehensive error handling
- Graceful degradation when API fails
- Full technical analysis even with cached data

## Files Structure

```
finance_utils/
├── stock_simple.py          # Simple, cache-first implementation
├── stock_robust.py          # Full-featured robust implementation
├── yahoo_finance_client.py  # Advanced API client
├── playground_fixed.py      # Working playground script
├── playground_simple.py     # Simple test script
├── test_robust.py          # Test suite
├── stock.py                # Original implementation
├── playground.py           # Original playground
└── README.md               # This file
```

## Quick Start

### Using the Simple Implementation (Recommended)
```python
from stock_simple import StockSimple

# Create stock instance
aapl = StockSimple("AAPL")

# Check if data is available
if aapl.is_valid():
    # Show company info
    aapl.describe()
    
    # Plot technical indicators
    aapl.plot_moving_averages()
    aapl.plot_rsi()
    aapl.plot_bollinger_bands()
    aapl.plot_macd()
    
    # Get summary
    aapl.summary()
    
    # Save data
    aapl.save_snapshot()
```

### Running the Playground
```bash
# Run the fixed playground script
python playground_fixed.py

# Or run the simple test
python playground_simple.py
```

## Features

### Technical Indicators
- **Moving Averages**: 50-day and 200-day
- **MACD**: Moving Average Convergence Divergence
- **RSI**: Relative Strength Index
- **Bollinger Bands**: Upper and lower bands
- **ATR**: Average True Range
- **OBV**: On-Balance Volume
- **Stochastic Oscillator**: %K and %D

### Stock Analysis
- **Trend Analysis**: Bullish/bearish indicators
- **Volatility Analysis**: Standard deviation of returns
- **Growth Calculation**: Period-over-period growth
- **Comparison Tools**: Compare multiple stocks

### Robust Features
- **Automatic Caching**: Saves data locally
- **Graceful Degradation**: Works with cached data
- **Error Handling**: Comprehensive error management
- **Rate Limit Handling**: Automatic retry with backoff
- **Authentication**: Proper crumb/cookie management

## Error Handling

The implementation handles common Yahoo Finance errors:

1. **429 Too Many Requests**: Automatic retry with exponential backoff
2. **Invalid Crumb**: Automatic token refresh
3. **JSON Decode Errors**: Fallback to cached data
4. **Network Issues**: Timeout handling and retries
5. **Empty Responses**: Graceful degradation

## Usage Examples

### Basic Stock Analysis
```python
from stock_simple import StockSimple

# Analyze Apple stock
aapl = StockSimple("AAPL")
if aapl.is_valid():
    print(f"Latest price: ${aapl.today()['Close']:.2f}")
    print(f"Is bullish: {aapl.is_bullish()}")
    aapl.plot_moving_averages()
```

### Comparing Stocks
```python
aapl = StockSimple("AAPL")
nvda = StockSimple("NVDA")

if aapl.is_valid() and nvda.is_valid():
    aapl.compare_with(nvda)
```

## API Rate Limiting Solutions

The implementation addresses Yahoo Finance rate limiting through:

1. **Caching**: Reduces API calls by using cached data
2. **Delays**: Adds delays between requests
3. **Retry Logic**: Automatically retries failed requests
4. **Session Management**: Maintains proper authentication
5. **Fallback**: Uses cached data when API fails

## Dependencies

```bash
pip install yfinance pandas matplotlib requests
```

## Best Practices

1. **Use Cached Data**: Always check if cached data is sufficient
2. **Implement Delays**: Add delays between API calls
3. **Handle Errors**: Always check `is_valid()` before using data
4. **Batch Operations**: Process multiple stocks with delays
5. **Monitor Rate Limits**: Watch for 429 errors and adjust accordingly
# Contributing

When contributing:
1. Test with rate-limited scenarios
2. Ensure backward compatibility
3. Add error handling for new features
4. Update documentation
5. Test with cached data scenarios

# License

Educational purposes only. Respect Yahoo Finance's terms when using their data.
