#!/usr/bin/env python3
"""
Script to check data freshness and generate comprehensive reports.
"""

from stock_simple import StockSimple
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

def check_data_freshness(stock):
    """Check how fresh the stock data is."""
    if not stock.is_valid():
        return None, "No data available"
    
    last_date = stock.history.index[-1].date()
    today = datetime.now().date()
    days_behind = (today - last_date).days
    
    # Market is closed on weekends
    # If today is Monday (0), weekend could make data up to 3 days old
    # If today is Tuesday (1), data should be at most 1 day old
    weekday = today.weekday()  # 0=Monday, 6=Sunday
    
    if weekday == 0:  # Monday
        acceptable_delay = 3
    elif weekday == 1:  # Tuesday  
        acceptable_delay = 1
    else:  # Wednesday-Sunday
        acceptable_delay = 1
    
    is_fresh = days_behind <= acceptable_delay
    
    status = "✅ Fresh" if is_fresh else "❌ Stale"
    
    return {
        "last_date": last_date.strftime("%Y-%m-%d"),
        "days_behind": days_behind,
        "is_fresh": is_fresh,
        "status": status,
        "data_points": len(stock.history)
    }, None

def generate_comprehensive_report(symbols=None):
    """Generate comprehensive stock analysis report."""
    if symbols is None:
        symbols = ["AAPL", "NVDA", "GOOGL", "MSFT", "TSLA"]
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "stocks": {},
        "summary": {
            "total_stocks": 0,
            "fresh_data": 0,
            "stale_data": 0,
            "no_data": 0
        }
    }
    
    print("🔍 Analyzing Stock Data Freshness and Generating Report")
    print("=" * 60)
    
    for symbol in symbols:
        print(f"\n📊 Analyzing {symbol}...")
        stock = StockSimple(symbol)
        
        freshness, error = check_data_freshness(stock)
        
        if error:
            print(f"❌ {symbol}: {error}")
            report["stocks"][symbol] = {
                "error": error,
                "valid": False
            }
            report["summary"]["no_data"] += 1
            continue
        
        print(f"📅 Data: {freshness['last_date']} ({freshness['days_behind']} days behind)")
        print(f"📈 Status: {freshness['status']}")
        print(f"📊 Data Points: {freshness['data_points']}")
        
        # Generate stock analysis
        stock_analysis = {
            "freshness": freshness,
            "valid": True,
            "basic_info": {
                "symbol": stock.ticker,
                "current_price": float(stock.today()["Close"]),
                "volume": int(stock.today()["Volume"]),
                "high": float(stock.today()["High"]),
                "low": float(stock.today()["Low"])
            },
            "technical_analysis": {
                "rsi": float(stock.today()["RSI"]),
                "macd": float(stock.today()["MACD"]),
                "ma_50": float(stock.today()["50MA"]),
                "ma_200": float(stock.today()["200MA"]),
                "upper_band": float(stock.today()["Upper Band"]),
                "lower_band": float(stock.today()["Lower Band"]),
                "atr": float(stock.today()["ATR"])
            },
            "performance": {
                "period_start": stock.history.index[0].date().strftime("%Y-%m-%d"),
                "period_end": stock.history.index[-1].date().strftime("%Y-%m-%d"),
                "growth_percent": ((stock.history["Close"].iloc[-1] - stock.history["Close"].iloc[0]) / stock.history["Close"].iloc[0]) * 100,
                "volatility": float(stock.history["Daily Return"].std()),
                "max_price": float(stock.history["Close"].max()),
                "min_price": float(stock.history["Close"].min())
            },
            "signals": {
                "is_bullish": stock.is_bullish(),
                "is_bearish": stock.is_bearish(),
                "price_above_ma50": stock.today()["Close"] > stock.today()["50MA"],
                "price_above_ma200": stock.today()["Close"] > stock.today()["200MA"],
                "rsi_overbought": stock.today()["RSI"] > 70,
                "rsi_oversold": stock.today()["RSI"] < 30
            }
        }
        
        report["stocks"][symbol] = stock_analysis
        report["summary"]["total_stocks"] += 1
        
        if freshness["is_fresh"]:
            report["summary"]["fresh_data"] += 1
        else:
            report["summary"]["stale_data"] += 1
        
        # Print key metrics
        print(f"💰 Price: ${stock_analysis['basic_info']['current_price']:.2f}")
        print(f"📊 RSI: {stock_analysis['technical_analysis']['rsi']:.1f}")
        print(f"📈 Growth: {stock_analysis['performance']['growth_percent']:.1f}%")
        print(f"🎯 Signals: {'🐂 Bullish' if stock_analysis['signals']['is_bullish'] else '🐻 Bearish' if stock_analysis['signals']['is_bearish'] else '➡️ Neutral'}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    print(f"Total Stocks Analyzed: {report['summary']['total_stocks']}")
    print(f"Fresh Data: {report['summary']['fresh_data']}")
    print(f"Stale Data: {report['summary']['stale_data']}")
    print(f"No Data: {report['summary']['no_data']}")
    
    # Save report
    report_file = f"stock_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Report saved to: {report_file}")
    
    return report

def main():
    """Main function to run data analysis."""
    print("🚀 Stock Data Analysis Tool")
    print("=" * 40)
    
    # Check specific stocks
    symbols = ["AAPL", "NVDA", "GOOGL", "MSFT", "TSLA"]
    
    # Generate comprehensive report
    report = generate_comprehensive_report(symbols)
    
    # Recommendations based on data freshness
    print("\n" + "=" * 60)
    print("🔧 RECOMMENDATIONS")
    print("=" * 60)
    
    if report["summary"]["stale_data"] > 0:
        print("⚠️  Some data is stale. Consider:")
        print("   • Waiting for market hours to try fresh data")
        print("   • Using cached data for historical analysis")
        print("   • Implementing data refresh strategies")
    
    if report["summary"]["fresh_data"] > 0:
        print("✅ Fresh data available for analysis")
    
    if report["summary"]["no_data"] > 0:
        print("❌ Some stocks have no data - check symbols and connectivity")
    
    print("\n🎯 Next Steps:")
    print("   • Use 'playground_fixed.py' for detailed analysis")
    print("   • Run Flask dashboard for interactive visualization")
    print("   • Generate custom reports for specific stocks")

if __name__ == "__main__":
    main()
