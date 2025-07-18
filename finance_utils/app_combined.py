#!/usr/bin/env python3
"""
Combined Flask Dashboard for Stock and Forex Data Visualization
"""

from flask import Flask, render_template, jsonify, request, send_file
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
import os
import io
import base64
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
matplotlib.use('Agg')  # Use non-interactive backend

# Import forex modules
# API Reference: Alpha Vantage Forex API Documentation
# https://www.alphavantage.co/documentation/
# For real-time forex data, exchange rates, and FX intraday data
from forex.forex_client import ForexClient
from forex.currency_pairs import (
    get_all_pairs, get_pairs_by_category, get_pair_info,
    get_most_active_pairs, MAJOR_PAIRS, MINOR_PAIRS, EXOTIC_PAIRS
)

app = Flask(__name__)

# Initialize forex client (demo mode)
forex_client = None
api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
if api_key:
    forex_client = ForexClient(api_key)

# Global cache for data
stock_cache = {}
forex_cache = {}

def get_mock_forex_data(pair='EUR/USD', days=30):
    """Generate mock forex data for demonstration"""
    if pair in forex_cache:
        return forex_cache[pair]
    
    # Generate realistic forex data
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=days),
        end=datetime.now(),
        freq='1h'
    )
    
    base_price = 1.0850 if 'EUR/USD' in pair else 1.2650
    n_periods = len(dates)
    
    # Random walk with drift
    returns = np.random.normal(0.0001, 0.001, n_periods)
    prices = base_price * np.exp(np.cumsum(returns))
    
    # Generate OHLC data
    data = []
    for i, price in enumerate(prices):
        high = price * (1 + np.random.uniform(0, 0.002))
        low = price * (1 - np.random.uniform(0, 0.002))
        open_price = prices[i-1] if i > 0 else price
        close_price = price
        
        data.append({
            'Open': open_price,
            'High': high,
            'Low': low,
            'Close': close_price,
            'Volume': np.random.randint(1000, 10000)
        })
    
    df = pd.DataFrame(data, index=dates)
    
    # Add technical indicators
    df['Daily Return'] = df['Close'].pct_change()
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    df['EMA_12'] = df['Close'].ewm(span=12).mean()
    df['EMA_26'] = df['Close'].ewm(span=26).mean()
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['Signal'] = df['MACD'].ewm(span=9).mean()
    df['Histogram'] = df['MACD'] - df['Signal']
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    df['BB_Std'] = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * 2)
    df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * 2)
    
    forex_cache[pair] = df
    return df

def create_forex_candlestick_chart(pair):
    """Create a candlestick chart for forex pair"""
    df = get_mock_forex_data(pair)
    df_recent = df.tail(100)  # Last 100 data points
    
    fig = go.Figure(data=[go.Candlestick(
        x=df_recent.index,
        open=df_recent['Open'],
        high=df_recent['High'],
        low=df_recent['Low'],
        close=df_recent['Close'],
        name=f"{pair} Price"
    )])
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=df_recent.index,
        y=df_recent['SMA_20'],
        mode='lines',
        name='SMA 20',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_recent.index,
        y=df_recent['SMA_50'],
        mode='lines',
        name='SMA 50',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f'{pair} Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_white',
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_forex_technical_chart(pair):
    """Create technical indicators chart for forex"""
    df = get_mock_forex_data(pair)
    df_recent = df.tail(100)
    
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('RSI', 'MACD', 'Bollinger Bands'),
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}],
               [{"secondary_y": False}],
               [{"secondary_y": False}]]
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['RSI'], name='RSI', 
                  line=dict(color='purple')),
        row=1, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['MACD'], name='MACD', 
                  line=dict(color='blue')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['Signal'], name='Signal', 
                  line=dict(color='red')),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=df_recent.index, y=df_recent['Histogram'], name='Histogram', 
               opacity=0.3),
        row=2, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['Close'], name='Close', 
                  line=dict(color='black')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['BB_Upper'], name='Upper Band', 
                  line=dict(color='red', dash='dash')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df_recent.index, y=df_recent['BB_Lower'], name='Lower Band', 
                  line=dict(color='green', dash='dash')),
        row=3, col=1
    )
    
    fig.update_layout(
        title=f'{pair} Technical Indicators',
        height=800,
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_forex_summary(pair):
    """Get forex pair summary"""
    df = get_mock_forex_data(pair)
    latest = df.iloc[-1]
    
    # Calculate statistics
    daily_returns = df['Daily Return'].dropna()
    volatility = daily_returns.std() * np.sqrt(252)  # Annualized
    
    return {
        'pair': pair,
        'current_price': round(float(latest['Close']), 4),
        'volume': int(latest['Volume']),
        'high': round(float(latest['High']), 4),
        'low': round(float(latest['Low']), 4),
        'rsi': round(float(latest['RSI']), 1),
        'macd': round(float(latest['MACD']), 4),
        'sma_20': round(float(latest['SMA_20']), 4),
        'sma_50': round(float(latest['SMA_50']), 4),
        'volatility': round(float(volatility), 4),
        'daily_return': round(float(daily_returns.iloc[-1]), 4),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'data_points': len(df)
    }

# Routes
@app.route('/')
def main_dashboard():
    """Main dashboard with mode switcher"""
    return render_template('combined_dashboard.html')

@app.route('/stocks')
def stocks_dashboard():
    """Stock dashboard"""
    # Create mock summary data
    summary = {
        'last_updated': '2025-07-18 12:00',
        'days_behind': 0,
        'current_price': 1500.00,
        'is_bullish': True,
        'is_bearish': False,
        'volatility': 0.02,
        'high': 1510.00,
        'low': 1480.00,
        'volume': 1000000,
        'growth_percent': 0.01,
        'rsi': 55.0,
        'macd': 0.5,
        'ma_50': 1450.00,
        'ma_200': 1400.00
    }

    return render_template('stock.html', symbol='AAPL', summary=summary)

@app.route('/forex')
def forex_dashboard():
    """Forex dashboard"""
    # Get currency pairs data
    major_pairs = get_pairs_by_category('major')
    minor_pairs = get_pairs_by_category('minor')
    exotic_pairs = get_pairs_by_category('exotic')
    
    # Get active pairs
    try:
        active_pairs = get_most_active_pairs()
    except:
        active_pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF']
    
    return render_template('forex/forex_dashboard.html',
                         major_pairs=major_pairs,
                         minor_pairs=minor_pairs,
                         exotic_pairs=exotic_pairs,
                         active_pairs=active_pairs)

@app.route('/forex/pair/<base>/<quote>')
def forex_pair_page(base, quote):
    """Individual forex pair page"""
    pair = f"{base}/{quote}"
    
    # Validate pair
    all_pairs = get_all_pairs()
    if pair not in all_pairs:
        return render_template('error.html', 
                             message=f"Forex pair {pair} not found")
    
    pair_info = get_pair_info(pair)
    summary = get_forex_summary(pair)
    candlestick_chart = create_forex_candlestick_chart(pair)
    technical_chart = create_forex_technical_chart(pair)
    
    return render_template('forex_pair.html',
                         pair=pair,
                         pair_info=pair_info,
                         summary=summary,
                         candlestick_chart=candlestick_chart,
                         technical_chart=technical_chart)

# API Routes
@app.route('/api/forex/pairs')
def api_forex_pairs():
    """API endpoint for forex pairs"""
    return jsonify({
        'major': list(MAJOR_PAIRS.keys()),
        'minor': list(MINOR_PAIRS.keys()),
        'exotic': list(EXOTIC_PAIRS.keys())
    })

@app.route('/api/forex/pair/<base>/<quote>')
def api_forex_pair(base, quote):
    """API endpoint for forex pair data"""
    pair = f"{base}/{quote}"
    
    if pair not in get_all_pairs():
        return jsonify({'error': f'Forex pair {pair} not found'}), 404
    
    summary = get_forex_summary(pair)
    return jsonify(summary)

@app.route('/api/forex/rates')
def api_forex_rates():
    """API endpoint for current forex rates"""
    pairs = ['EUR/USD', 'GBP/USD', 'USD/JPY', 'USD/CHF', 'AUD/USD']
    rates = {}
    
    for pair in pairs:
        summary = get_forex_summary(pair)
        rates[pair] = {
            'rate': summary['current_price'],
            'change': summary['daily_return']
        }
    
    return jsonify(rates)

@app.route('/api/forex/sessions')
def api_forex_sessions():
    """API endpoint for forex trading sessions"""
    return jsonify({
        'sydney': {'open': '22:00', 'close': '07:00', 'active': False},
        'tokyo': {'open': '00:00', 'close': '09:00', 'active': False},
        'london': {'open': '08:00', 'close': '17:00', 'active': True},
        'new_york': {'open': '13:00', 'close': '22:00', 'active': True}
    })

@app.route('/api/forex/overview')
def api_forex_overview():
    """API endpoint for forex market overview"""
    return jsonify({
        'total_pairs': 28,
        'active_sessions': 2,
        'top_movers': [
            {'pair': 'EUR/USD', 'change': 0.0012},
            {'pair': 'GBP/USD', 'change': -0.0008},
            {'pair': 'USD/JPY', 'change': 0.0015}
        ],
        'market_sentiment': 'bullish',
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'forex_enabled': True,
        'stocks_enabled': True,
        'mode': 'demo'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    print("🚀 Starting Combined Stock & Forex Dashboard")
    print("=" * 50)
    print("📊 Available endpoints:")
    print("  - Main Dashboard: http://localhost:5001/")
    print("  - Stock Dashboard: http://localhost:5001/stocks")
    print("  - Forex Dashboard: http://localhost:5001/forex")
    print("  - Forex Pair: http://localhost:5001/forex/pair/EUR/USD")
    print("  - API Status: http://localhost:5001/api/status")
    print("  - Forex Rates API: http://localhost:5001/api/forex/rates")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
