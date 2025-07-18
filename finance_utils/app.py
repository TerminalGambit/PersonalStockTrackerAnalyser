#!/usr/bin/env python3
"""
Flask Dashboard for Stock Data Visualization
"""

from flask import Flask, render_template, jsonify, request, send_file
from stock_simple import StockSimple
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
matplotlib.use('Agg')  # Use non-interactive backend

app = Flask(__name__)

# Global cache for stock data
stock_cache = {}

def get_stock_data(symbol, force_refresh=False):
    """Get stock data with caching."""
    if symbol not in stock_cache or force_refresh:
        stock_cache[symbol] = StockSimple(symbol)
    return stock_cache[symbol]

def create_candlestick_chart(stock):
    """Create a candlestick chart using Plotly."""
    if not stock.is_valid():
        return None
    
    df = stock.history.tail(100)  # Last 100 days
    
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name=f"{stock.ticker} Price"
    )])
    
    # Add moving averages
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['50MA'],
        mode='lines',
        name='50-Day MA',
        line=dict(color='orange', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['200MA'],
        mode='lines',
        name='200-Day MA',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f'{stock.ticker} Stock Price with Moving Averages',
        xaxis_title='Date',
        yaxis_title='Price ($)',
        template='plotly_white',
        height=500
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_technical_indicators_chart(stock):
    """Create technical indicators chart."""
    if not stock.is_valid():
        return None
    
    df = stock.history.tail(100)
    
    # Create subplots
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
        go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
        row=1, col=1
    )
    fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
    
    # MACD
    fig.add_trace(
        go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='red')),
        row=2, col=1
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df['Histogram'], name='Histogram', opacity=0.3),
        row=2, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name='Close', line=dict(color='black')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Upper Band'], name='Upper Band', 
                  line=dict(color='red', dash='dash')),
        row=3, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Lower Band'], name='Lower Band', 
                  line=dict(color='green', dash='dash')),
        row=3, col=1
    )
    
    fig.update_layout(
        title=f'{stock.ticker} Technical Indicators',
        height=800,
        template='plotly_white'
    )
    
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def get_stock_summary(stock):
    """Get stock summary data."""
    if not stock.is_valid():
        return None
    
    latest = stock.today()
    
    # Calculate data freshness
    last_date = stock.history.index[-1].date()
    today = datetime.now().date()
    days_behind = (today - last_date).days
    
    return {
        'symbol': stock.ticker,
        'current_price': round(float(latest['Close']), 2),
        'volume': int(latest['Volume']),
        'high': round(float(latest['High']), 2),
        'low': round(float(latest['Low']), 2),
        'rsi': round(float(latest['RSI']), 1),
        'macd': round(float(latest['MACD']), 3),
        'ma_50': round(float(latest['50MA']), 2),
        'ma_200': round(float(latest['200MA']), 2),
        'growth_percent': round(((stock.history["Close"].iloc[-1] - stock.history["Close"].iloc[0]) / stock.history["Close"].iloc[0]) * 100, 2),
        'volatility': round(float(stock.history["Daily Return"].std()), 4),
        'is_bullish': bool(stock.is_bullish()),
        'is_bearish': bool(stock.is_bearish()),
        'last_updated': last_date.strftime('%Y-%m-%d'),
        'days_behind': days_behind,
        'data_points': len(stock.history)
    }

@app.route('/')
def dashboard():
    """Main dashboard page."""
    return render_template('dashboard.html')

@app.route('/stock/<symbol>')
def stock_page(symbol):
    """Individual stock page."""
    stock = get_stock_data(symbol.upper())
    
    if not stock.is_valid():
        return render_template('error.html', 
                             message=f"No data available for {symbol.upper()}")
    
    summary = get_stock_summary(stock)
    candlestick_chart = create_candlestick_chart(stock)
    technical_chart = create_technical_indicators_chart(stock)
    
    return render_template('stock.html', 
                         symbol=symbol.upper(),
                         summary=summary,
                         candlestick_chart=candlestick_chart,
                         technical_chart=technical_chart)

@app.route('/api/stock/<symbol>')
def api_stock_data(symbol):
    """API endpoint for stock data."""
    stock = get_stock_data(symbol.upper())
    
    if not stock.is_valid():
        return jsonify({'error': f'No data available for {symbol.upper()}'}), 404
    
    summary = get_stock_summary(stock)
    return jsonify(summary)

@app.route('/api/stocks')
def api_stocks_list():
    """API endpoint for available stocks."""
    available_stocks = []
    symbols = ['AAPL', 'NVDA', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META']
    
    for symbol in symbols:
        stock = get_stock_data(symbol)
        if stock.is_valid():
            summary = get_stock_summary(stock)
            available_stocks.append(summary)
    
    return jsonify(available_stocks)

@app.route('/api/compare')
def api_compare():
    """API endpoint for stock comparison."""
    symbols = request.args.get('symbols', '').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    if len(symbols) < 2:
        return jsonify({'error': 'At least 2 symbols required'}), 400
    
    comparison_data = []
    
    for symbol in symbols:
        stock = get_stock_data(symbol)
        if stock.is_valid():
            summary = get_stock_summary(stock)
            comparison_data.append(summary)
    
    return jsonify(comparison_data)

@app.route('/compare')
def compare_page():
    """Stock comparison page."""
    return render_template('compare.html')

@app.route('/api/refresh/<symbol>')
def api_refresh_stock(symbol):
    """API endpoint to refresh stock data."""
    try:
        stock = get_stock_data(symbol.upper(), force_refresh=True)
        if stock.is_valid():
            summary = get_stock_summary(stock)
            return jsonify({'success': True, 'data': summary})
        else:
            return jsonify({'success': False, 'error': 'Failed to refresh data'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/reports')
def reports_page():
    """Reports page."""
    return render_template('reports.html')

@app.route('/api/generate_report')
def api_generate_report():
    """Generate comprehensive report."""
    symbols = request.args.get('symbols', 'AAPL,NVDA').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    report_data = []
    
    for symbol in symbols:
        stock = get_stock_data(symbol)
        if stock.is_valid():
            summary = get_stock_summary(stock)
            
            # Add additional analysis
            latest = stock.today()
            summary.update({
                'technical_signals': {
                    'price_above_ma50': bool(latest['Close'] > latest['50MA']),
                    'price_above_ma200': bool(latest['Close'] > latest['200MA']),
                    'rsi_overbought': bool(latest['RSI'] > 70),
                    'rsi_oversold': bool(latest['RSI'] < 30),
                    'macd_bullish': bool(latest['MACD'] > latest['Signal'])
                },
                'price_levels': {
                    'support': round(float(latest['Lower Band']), 2),
                    'resistance': round(float(latest['Upper Band']), 2),
                    'atr': round(float(latest['ATR']), 2)
                }
            })
            
            report_data.append(summary)
    
    return jsonify({
        'generated_at': datetime.now().isoformat(),
        'stocks': report_data,
        'summary': {
            'total_analyzed': len(report_data),
            'bullish_count': sum(1 for s in report_data if s['is_bullish']),
            'bearish_count': sum(1 for s in report_data if s['is_bearish'])
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
