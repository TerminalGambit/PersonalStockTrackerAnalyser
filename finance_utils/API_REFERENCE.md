# Financial Analytics Hub - API Reference

## Overview

The Financial Analytics Hub provides comprehensive forex and stock market analysis through a RESTful API. This documentation covers all available endpoints, their parameters, and response formats.

### Base URL
```
http://localhost:5001
```

### API Reference
For real-time forex data, this application uses principles from the Alpha Vantage API:
- **Documentation**: https://www.alphavantage.co/documentation/
- **Forex API**: https://www.alphavantage.co/documentation/#fx
- **Technical Indicators**: https://www.alphavantage.co/documentation/#technical-indicators

---

## Endpoints

### 1. System Status

#### GET `/api/status`
Returns the current system status and configuration.

**Response:**
```json
{
  "status": "running",
  "timestamp": "2025-07-18T15:30:00.000Z",
  "forex_enabled": true,
  "stocks_enabled": true,
  "mode": "demo"
}
```

---

### 2. Forex Endpoints

#### GET `/api/forex/pairs`
Returns all available forex currency pairs organized by category.

**Parameters:**
- `category` (optional): Filter by category (`major`, `minor`, `exotic`)

**Response:**
```json
{
  "major": ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF"],
  "minor": ["EUR/GBP", "EUR/JPY", "GBP/JPY", "AUD/NZD"],
  "exotic": ["USD/TRY", "EUR/TRY", "GBP/TRY", "USD/ZAR"]
}
```

#### GET `/api/forex/rates`
Returns current exchange rates for major currency pairs.

**Response:**
```json
{
  "EUR/USD": {
    "rate": 1.0850,
    "change": 0.0012
  },
  "GBP/USD": {
    "rate": 1.2650,
    "change": -0.0008
  }
}
```

#### GET `/api/forex/overview`
Returns forex market overview with summary statistics.

**Response:**
```json
{
  "total_pairs": 28,
  "active_sessions": 2,
  "top_movers": [
    {
      "pair": "EUR/USD",
      "change": 0.0012
    }
  ],
  "market_sentiment": "bullish",
  "last_updated": "2025-07-18 15:30:00"
}
```

#### GET `/api/forex/sessions`
Returns forex trading session information.

**Response:**
```json
{
  "sydney": {
    "open": "22:00",
    "close": "07:00",
    "active": false
  },
  "tokyo": {
    "open": "00:00",
    "close": "09:00",
    "active": false
  },
  "london": {
    "open": "08:00",
    "close": "17:00",
    "active": true
  },
  "new_york": {
    "open": "13:00",
    "close": "22:00",
    "active": true
  }
}
```

#### GET `/api/forex/pair/<base>/<quote>`
Returns detailed data for a specific forex pair.

**Parameters:**
- `base`: Base currency code (e.g., EUR)
- `quote`: Quote currency code (e.g., USD)

**Example:** `/api/forex/pair/EUR/USD`

**Response:**
```json
{
  "pair": "EUR/USD",
  "current_price": 1.0850,
  "volume": 5000,
  "high": 1.0875,
  "low": 1.0825,
  "rsi": 55.0,
  "macd": 0.0012,
  "sma_20": 1.0840,
  "sma_50": 1.0820,
  "volatility": 0.0234,
  "daily_return": 0.0012,
  "last_updated": "2025-07-18 15:30:00",
  "data_points": 720
}
```

---

## Web Interface Endpoints

### Main Dashboard
- **GET** `/` - Combined dashboard with overview of all markets

### Stock Analysis
- **GET** `/stocks` - Stock analysis dashboard

### Forex Analysis
- **GET** `/forex` - Forex trading dashboard
- **GET** `/forex/pair/<base>/<quote>` - Individual forex pair analysis page

---

## Error Handling

All API endpoints return appropriate HTTP status codes:

- **200 OK**: Successful request
- **404 Not Found**: Resource not found (e.g., invalid forex pair)
- **500 Internal Server Error**: Server error

Error responses include a JSON object with error details:
```json
{
  "error": "Forex pair XXX/YYY not found"
}
```

---

## Rate Limiting

The API includes built-in rate limiting to prevent abuse:
- Default delay: 12 seconds between requests
- Automatic retry with exponential backoff
- Request count tracking

---

## Data Sources

- **Forex Data**: Mock data generated for demonstration purposes
- **Technical Indicators**: RSI, MACD, SMA, Bollinger Bands
- **Real-time Integration**: Designed for Alpha Vantage API compatibility

---

## Testing

Comprehensive test suites are available:
- `test_forex_api.py` - Basic API endpoint tests
- `test_forex_api_comprehensive.py` - Comprehensive testing including performance and validation

Run tests with:
```bash
python3 test_forex_api_comprehensive.py
```

---

## Example Usage

### Python
```python
import requests

# Get forex rates
response = requests.get('http://localhost:5001/api/forex/rates')
rates = response.json()
print(f"EUR/USD: {rates['EUR/USD']['rate']}")

# Get specific pair data
response = requests.get('http://localhost:5001/api/forex/pair/EUR/USD')
pair_data = response.json()
print(f"RSI: {pair_data['rsi']}")
```

### JavaScript
```javascript
// Get forex overview
fetch('/api/forex/overview')
  .then(response => response.json())
  .then(data => {
    console.log('Market sentiment:', data.market_sentiment);
    console.log('Active sessions:', data.active_sessions);
  });
```

### cURL
```bash
# Get system status
curl http://localhost:5001/api/status

# Get EUR/USD data
curl http://localhost:5001/api/forex/pair/EUR/USD
```

---

## Support

For issues or questions:
1. Check the test files for usage examples
2. Review the Alpha Vantage API documentation for data concepts
3. Examine the Flask application code for implementation details

---

*Last updated: July 18, 2025*
