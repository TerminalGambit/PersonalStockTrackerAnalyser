#!/usr/bin/env python3
"""
Flask Dashboard for Stock Data Visualization using Alpha Vantage
"""

from flask import Flask, render_template, jsonify, request, send_file
from alpha_vantage_adapter import AlphaVantageManager, AlphaVantageStock
from latex_report_generator import LatexReportGenerator
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

# Initialize Alpha Vantage manager
av_manager = AlphaVantageManager()

# Initialize LaTeX report generator
latex_generator = LatexReportGenerator()

def get_stock_data(symbol, force_refresh=False):
    """Get stock data using Alpha Vantage"""
    if force_refresh or symbol not in av_manager.stocks:
        return av_manager.get_stock(symbol)
    return av_manager.stocks[symbol]

def create_candlestick_chart(stock):
    """Create a candlestick chart using Plotly"""
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
    if '50MA' in df.columns:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['50MA'],
            mode='lines',
            name='50-Day MA',
            line=dict(color='orange', width=2)
        ))
    
    if '200MA' in df.columns:
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
    """Create technical indicators chart"""
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
    if 'RSI' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['RSI'], name='RSI', line=dict(color='purple')),
            row=1, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=1, col=1)
    
    # MACD
    if 'MACD' in df.columns:
        fig.add_trace(
            go.Scatter(x=df.index, y=df['MACD'], name='MACD', line=dict(color='blue')),
            row=2, col=1
        )
        if 'Signal' in df.columns:
            fig.add_trace(
                go.Scatter(x=df.index, y=df['Signal'], name='Signal', line=dict(color='red')),
                row=2, col=1
            )
        if 'Histogram' in df.columns:
            fig.add_trace(
                go.Bar(x=df.index, y=df['Histogram'], name='Histogram', opacity=0.3),
                row=2, col=1
            )
    
    # Bollinger Bands
    if 'Upper Band' in df.columns:
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
    """Get stock summary data"""
    if not stock.is_valid():
        return None
    
    return av_manager.get_stock_summary(stock.ticker)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/stock/<symbol>')
def stock_page(symbol):
    """Individual stock page"""
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
    """API endpoint for stock data"""
    stock = get_stock_data(symbol.upper())
    
    if not stock.is_valid():
        return jsonify({'error': f'No data available for {symbol.upper()}'}), 404
    
    summary = get_stock_summary(stock)
    return jsonify(summary)

@app.route('/api/stocks')
def api_stocks_list():
    """API endpoint for available stocks"""
    available_stocks = []
    symbols = ['AAPL', 'NVDA', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'META']
    
    for symbol in symbols:
        try:
            stock = get_stock_data(symbol)
            if stock.is_valid():
                summary = get_stock_summary(stock)
                available_stocks.append(summary)
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
    
    return jsonify(available_stocks)

@app.route('/api/compare')
def api_compare():
    """API endpoint for stock comparison"""
    symbols = request.args.get('symbols', '').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    if len(symbols) < 2:
        return jsonify({'error': 'At least 2 symbols required'}), 400
    
    comparison_data = []
    
    for symbol in symbols:
        try:
            stock = get_stock_data(symbol)
            if stock.is_valid():
                summary = get_stock_summary(stock)
                comparison_data.append(summary)
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
    
    return jsonify(comparison_data)

@app.route('/api/refresh/<symbol>')
def api_refresh_stock(symbol):
    """API endpoint to refresh stock data"""
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
    """Reports page"""
    return render_template('reports.html')

@app.route('/api/generate_report')
def api_generate_report():
    """Generate comprehensive report"""
    symbols = request.args.get('symbols', 'AAPL,NVDA').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    
    report_data = []
    
    for symbol in symbols:
        try:
            stock = get_stock_data(symbol)
            if stock.is_valid():
                summary = get_stock_summary(stock)
                
                # Add additional analysis
                latest = stock.today()
                
                # Check for None values before comparisons
                technical_signals = {}
                if summary['ma_50'] is not None:
                    technical_signals['price_above_ma50'] = summary['current_price'] > summary['ma_50']
                if summary['ma_200'] is not None:
                    technical_signals['price_above_ma200'] = summary['current_price'] > summary['ma_200']
                if summary['rsi'] is not None:
                    technical_signals['rsi_overbought'] = summary['rsi'] > 70
                    technical_signals['rsi_oversold'] = summary['rsi'] < 30
                if summary['macd'] is not None and 'Signal' in latest:
                    technical_signals['macd_bullish'] = float(latest['MACD']) > float(latest['Signal'])
                
                price_levels = {}
                if 'Upper Band' in latest and pd.notna(latest['Upper Band']):
                    price_levels['resistance'] = round(float(latest['Upper Band']), 2)
                if 'Lower Band' in latest and pd.notna(latest['Lower Band']):
                    price_levels['support'] = round(float(latest['Lower Band']), 2)
                if 'ATR' in latest and pd.notna(latest['ATR']):
                    price_levels['atr'] = round(float(latest['ATR']), 2)
                
                summary.update({
                    'technical_signals': technical_signals,
                    'price_levels': price_levels
                })
                
                report_data.append(summary)
        except Exception as e:
            print(f"Error generating report for {symbol}: {e}")
    
    return jsonify({
        'generated_at': datetime.now().isoformat(),
        'stocks': report_data,
        'summary': {
            'total_analyzed': len(report_data),
            'bullish_count': sum(1 for s in report_data if s['is_bullish']),
            'bearish_count': sum(1 for s in report_data if s['is_bearish']),
            'api_requests_used': av_manager.request_count,
            'api_requests_remaining': 500 - av_manager.request_count
        }
    })

@app.route('/api/generate_latex_report')
def api_generate_latex_report():
    """Generate LaTeX/PDF report"""
    symbols = request.args.get('symbols', 'AAPL').split(',')
    symbols = [s.strip().upper() for s in symbols if s.strip()]
    report_type = request.args.get('type', 'comprehensive')
    
    try:
        pdf_path, message = latex_generator.generate_report(symbols, report_type)
        
        if pdf_path:
            return jsonify({
                'success': True,
                'message': message,
                'pdf_path': str(pdf_path),
                'symbols': symbols,
                'report_type': report_type,
                'generated_at': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error generating LaTeX report: {str(e)}'
        }), 500

@app.route('/api/download_report')
def api_download_report():
    """Download the most recent PDF report"""
    report_path = request.args.get('path')
    
    if not report_path:
        return jsonify({'error': 'No report path specified'}), 400
    
    try:
        # Security check - ensure the path is within our reports directory
        report_path = os.path.abspath(report_path)
        reports_dir = os.path.abspath(latex_generator.output_dir)
        
        if not report_path.startswith(reports_dir):
            return jsonify({'error': 'Invalid report path'}), 400
        
        if not os.path.exists(report_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        # Determine filename for download
        filename = os.path.basename(report_path)
        
        return send_file(
            report_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error downloading report: {str(e)}'}), 500

@app.route('/api/list_reports')
def api_list_reports():
    """List all available reports"""
    try:
        reports = []
        reports_dir = latex_generator.output_dir
        
        if reports_dir.exists():
            for report_dir in reports_dir.iterdir():
                if report_dir.is_dir():
                    pdf_file = report_dir / 'report.pdf'
                    tex_file = report_dir / 'report.tex'
                    
                    if pdf_file.exists() or tex_file.exists():
                        # Extract info from directory name
                        parts = report_dir.name.split('_')
                        if len(parts) >= 3:
                            if parts[0] == 'multi':
                                symbols = 'Multiple'
                            else:
                                symbols = parts[0]
                            
                            timestamp = '_'.join(parts[-2:])
                            
                            reports.append({
                                'name': report_dir.name,
                                'symbols': symbols,
                                'timestamp': timestamp,
                                'has_pdf': pdf_file.exists(),
                                'has_tex': tex_file.exists(),
                                'pdf_path': str(pdf_file) if pdf_file.exists() else None,
                                'tex_path': str(tex_file) if tex_file.exists() else None
                            })
        
        # Sort by timestamp (most recent first)
        reports.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'reports': reports,
            'total': len(reports)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error listing reports: {str(e)}'}), 500

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify({
        'data_source': 'Alpha Vantage',
        'api_key_configured': av_manager.api_key is not None,
        'requests_made': av_manager.request_count,
        'requests_remaining': 500 - av_manager.request_count,
        'cached_stocks': list(av_manager.stocks.keys()),
        'rate_limit_delay': av_manager.rate_limit_delay
    })

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', message="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', message="Internal server error"), 500

if __name__ == '__main__':
    # Check if API key is configured
    if not av_manager.api_key:
        print("⚠️  Warning: No Alpha Vantage API key configured!")
        print("   Set the ALPHA_VANTAGE_API_KEY environment variable")
        print("   or get a free key from: https://www.alphavantage.co/support/#api-key")
    else:
        print(f"✅ Alpha Vantage API key configured: {av_manager.api_key[:8]}...")
        print(f"📊 Rate limit: {av_manager.rate_limit_delay} seconds between requests")
        print(f"📋 Daily limit: 500 requests")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
