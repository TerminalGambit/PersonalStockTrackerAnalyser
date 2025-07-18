#!/usr/bin/env python3
"""
Enhanced LaTeX Report Generator for Stock Analysis
Compatible with Alpha Vantage Flask Dashboard
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import pickle
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from alpha_vantage_adapter import AlphaVantageManager, AlphaVantageStock

# Load favorite stocks from config
try:
    with open('config.json') as config_file:
        config = json.load(config_file)
    FAVORITE_STOCKS = config.get('favorite_stocks', [])
except FileNotFoundError:
    print("⚠️ config.json not found. Using default stocks.")
    FAVORITE_STOCKS = ['AAPL', 'MSFT', 'GOOGL']

class LatexReportGenerator:
    def __init__(self, output_dir="latex_reports", cache_dir=".stock_cache", auto_open=True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.auto_open = auto_open
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self.av_manager = AlphaVantageManager()
        
        # Set up matplotlib for better plots
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.dpi'] = 300
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['font.size'] = 10
        
    def generate_report(self, symbols, report_type="comprehensive"):
        """
        Generate a LaTeX report for given symbols
        
        Args:
            symbols: List of stock symbols or single symbol
            report_type: 'comprehensive', 'summary', 'technical'
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        if len(symbols) == 1:
            report_name = f"{symbols[0]}_{timestamp}"
        else:
            report_name = f"multi_stock_{timestamp}"
        
        report_dir = self.output_dir / report_name
        report_dir.mkdir(exist_ok=True)
        
        # Generate report data
        report_data = self._collect_stock_data(symbols)
        if not report_data:
            return None, "No valid stock data found"
        
        # Create plots
        plot_paths = self._generate_plots(report_data, report_dir)
        
        # Generate LaTeX content
        latex_content = self._generate_latex_content(
            report_data, plot_paths, report_type
        )
        
        # Write LaTeX file
        tex_file = report_dir / "report.tex"
        with open(tex_file, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        # Compile to PDF
        pdf_path = self._compile_latex(tex_file)
        
        # Auto-open PDF if successful and requested
        if pdf_path and pdf_path.suffix == '.pdf' and self.auto_open:
            self._open_pdf(pdf_path)
        
        return pdf_path, "Report generated successfully"
    
    def _get_cache_path(self, symbol):
        """Get cache file path for a symbol"""
        return self.cache_dir / f"{symbol}_cache.pkl"
    
    def _is_cache_valid(self, cache_path):
        """Check if cache file is still valid"""
        if not cache_path.exists():
            return False
        
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        return datetime.now() - cache_time < self.cache_duration
    
    def _load_from_cache(self, symbol):
        """Load stock data from cache"""
        cache_path = self._get_cache_path(symbol)
        
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    print(f"📋 Loading cached data for {symbol}")
                    return cached_data
            except Exception as e:
                print(f"⚠️ Error loading cache for {symbol}: {e}")
                return None
        return None
    
    def _save_to_cache(self, symbol, data):
        """Save stock data to cache"""
        cache_path = self._get_cache_path(symbol)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 Cached data for {symbol}")
        except Exception as e:
            print(f"⚠️ Error saving cache for {symbol}: {e}")
    
    def _collect_stock_data(self, symbols):
        """Collect stock data for all symbols with caching"""
        report_data = []
        
        for symbol in symbols:
            try:
                # Try to load from cache first
                cached_data = self._load_from_cache(symbol)
                if cached_data:
                    report_data.append(cached_data)
                    continue
                
                # Fetch fresh data
                stock = self.av_manager.get_stock(symbol)
                if stock.is_valid():
                    summary = self.av_manager.get_stock_summary(symbol)
                    
                    # Add additional analysis
                    latest = stock.today()
                    
                    # Technical signals
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
                    
                    # Price levels
                    price_levels = {}
                    if 'Upper Band' in latest and pd.notna(latest['Upper Band']):
                        price_levels['resistance'] = round(float(latest['Upper Band']), 2)
                    if 'Lower Band' in latest and pd.notna(latest['Lower Band']):
                        price_levels['support'] = round(float(latest['Lower Band']), 2)
                    if 'ATR' in latest and pd.notna(latest['ATR']):
                        price_levels['atr'] = round(float(latest['ATR']), 2)
                    
                    stock_data = {
                        'symbol': symbol,
                        'stock': stock,
                        'summary': summary,
                        'technical_signals': technical_signals,
                        'price_levels': price_levels,
                        'latest': latest
                    }
                    
                    # Save to cache
                    self._save_to_cache(symbol, stock_data)
                    report_data.append(stock_data)
                    
            except Exception as e:
                print(f"Error collecting data for {symbol}: {e}")
                continue
        
        return report_data
    
    def _generate_plots(self, report_data, report_dir):
        """Generate all plots for the report"""
        plot_paths = {}
        
        for data in report_data:
            symbol = data['symbol']
            stock = data['stock']
            df = stock.history
            
            # Price and Moving Averages
            price_path = report_dir / f"{symbol}_price_chart.png"
            self._create_price_chart(df, symbol, price_path)
            
            # Technical Indicators
            tech_path = report_dir / f"{symbol}_technical.png"
            self._create_technical_chart(df, symbol, tech_path)
            
            # Bollinger Bands
            bb_path = report_dir / f"{symbol}_bollinger.png"
            self._create_bollinger_chart(df, symbol, bb_path)
            
            # Volume Chart
            volume_path = report_dir / f"{symbol}_volume.png"
            self._create_volume_chart(df, symbol, volume_path)
            
            plot_paths[symbol] = {
                'price': price_path.name,
                'technical': tech_path.name,
                'bollinger': bb_path.name,
                'volume': volume_path.name
            }
        
        return plot_paths
    
    def _create_price_chart(self, df, symbol, output_path):
        """Create price chart with moving averages"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot price
        ax.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='#1f77b4')
        
        # Plot moving averages if available
        if '50MA' in df.columns:
            ax.plot(df.index, df['50MA'], label='50-Day MA', linewidth=1.5, color='orange', alpha=0.8)
        if '200MA' in df.columns:
            ax.plot(df.index, df['200MA'], label='200-Day MA', linewidth=1.5, color='red', alpha=0.8)
        
        ax.set_title(f'{symbol} - Price Chart with Moving Averages', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
    
    def _create_technical_chart(self, df, symbol, output_path):
        """Create technical indicators chart"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
        
        # RSI
        if 'RSI' in df.columns:
            ax1.plot(df.index, df['RSI'], color='purple', linewidth=2)
            ax1.axhline(y=70, color='red', linestyle='--', alpha=0.7, label='Overbought')
            ax1.axhline(y=30, color='green', linestyle='--', alpha=0.7, label='Oversold')
            ax1.fill_between(df.index, 30, 70, alpha=0.1, color='gray')
            ax1.set_title('RSI (14)', fontweight='bold')
            ax1.set_ylabel('RSI')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # MACD
        if 'MACD' in df.columns:
            ax2.plot(df.index, df['MACD'], label='MACD', color='blue', linewidth=2)
            if 'Signal' in df.columns:
                ax2.plot(df.index, df['Signal'], label='Signal', color='red', linewidth=2)
            if 'Histogram' in df.columns:
                ax2.bar(df.index, df['Histogram'], alpha=0.3, color='gray', label='Histogram')
            ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            ax2.set_title('MACD', fontweight='bold')
            ax2.set_ylabel('MACD')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # ATR
        if 'ATR' in df.columns:
            ax3.plot(df.index, df['ATR'], color='orange', linewidth=2)
            ax3.set_title('Average True Range (ATR)', fontweight='bold')
            ax3.set_ylabel('ATR')
            ax3.grid(True, alpha=0.3)
        
        # Stochastic
        if '%K' in df.columns and '%D' in df.columns:
            ax4.plot(df.index, df['%K'], label='%K', color='blue', linewidth=2)
            ax4.plot(df.index, df['%D'], label='%D', color='red', linewidth=2)
            ax4.axhline(y=80, color='red', linestyle='--', alpha=0.7)
            ax4.axhline(y=20, color='green', linestyle='--', alpha=0.7)
            ax4.set_title('Stochastic Oscillator', fontweight='bold')
            ax4.set_ylabel('Stochastic')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
        
        plt.suptitle(f'{symbol} - Technical Indicators', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
    
    def _create_bollinger_chart(self, df, symbol, output_path):
        """Create Bollinger Bands chart"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot price
        ax.plot(df.index, df['Close'], label='Close Price', linewidth=2, color='#1f77b4')
        
        # Plot Bollinger Bands if available
        if all(col in df.columns for col in ['Upper Band', 'Lower Band', 'Middle Band']):
            ax.plot(df.index, df['Upper Band'], label='Upper Band', linewidth=1.5, color='red', alpha=0.8)
            ax.plot(df.index, df['Lower Band'], label='Lower Band', linewidth=1.5, color='green', alpha=0.8)
            ax.plot(df.index, df['Middle Band'], label='Middle Band (20MA)', linewidth=1.5, color='orange', alpha=0.8)
            
            # Fill between bands
            ax.fill_between(df.index, df['Lower Band'], df['Upper Band'], alpha=0.1, color='gray')
        
        ax.set_title(f'{symbol} - Bollinger Bands', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
    
    def _create_volume_chart(self, df, symbol, output_path):
        """Create volume chart"""
        fig, ax = plt.subplots(figsize=(12, 4))
        
        # Create volume bars with color coding
        colors = ['green' if close >= open_price else 'red' 
                 for close, open_price in zip(df['Close'], df['Open'])]
        
        ax.bar(df.index, df['Volume'], color=colors, alpha=0.7)
        ax.set_title(f'{symbol} - Volume', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Volume', fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Format y-axis for volume
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1e6:.1f}M'))
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(output_path, bbox_inches='tight', dpi=300)
        plt.close()
    
    def _generate_latex_content(self, report_data, plot_paths, report_type):
        """Generate LaTeX content based on report type"""
        timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")
        
        # Header
        latex_content = r"""
\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{xcolor}
\usepackage{fancyhdr}
\usepackage{titlesec}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{hyperref}

% Custom colors
\definecolor{bullish}{RGB}{0,128,0}
\definecolor{bearish}{RGB}{255,0,0}
\definecolor{neutral}{RGB}{128,128,128}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\textbf{Stock Analysis Report}}
\fancyhead[R]{\today}
\fancyfoot[C]{\thepage}

% Title formatting
\titleformat{\section}{\Large\bfseries\color{blue}}{\thesection}{1em}{}
\titleformat{\subsection}{\large\bfseries\color{blue}}{\thesubsection}{1em}{}

\begin{document}

% Title page
\begin{titlepage}
\centering
\vspace*{2cm}
{\Huge\bfseries Stock Analysis Report}

\vspace{1cm}
{\Large Professional Technical Analysis}

\vspace{2cm}
"""
        
        # Add symbols to title
        symbol_list = [data['symbol'] for data in report_data]
        if len(symbol_list) == 1:
            latex_content += f"{{\\LARGE\\textbf{{{symbol_list[0]}}}}}\n\n"
        else:
            latex_content += f"{{\\LARGE\\textbf{{Multi-Stock Analysis}}}}\n\n"
            latex_content += f"{{\\large Symbols: {', '.join(symbol_list)}}}\n\n"
        
        latex_content += r"""
\vspace{2cm}
{\large Generated on """ + timestamp + r"""}

\vspace{1cm}
{\large Alpha Vantage Data Source}

\vfill
\end{titlepage}

\tableofcontents
\newpage

"""
        
        # Executive Summary
        latex_content += self._generate_executive_summary(report_data)
        
        # Individual stock analysis
        for data in report_data:
            latex_content += self._generate_stock_section(data, plot_paths[data['symbol']])
        
        # Market Analysis (if multiple stocks)
        if len(report_data) > 1:
            latex_content += self._generate_market_analysis(report_data)
        
        # Conclusion
        latex_content += self._generate_conclusion(report_data)
        
        latex_content += r"""
\end{document}
"""
        
        return latex_content
    
    def _generate_executive_summary(self, report_data):
        """Generate executive summary section"""
        content = r"""
\section{Executive Summary}

This report provides a comprehensive technical analysis of the selected stocks using Alpha Vantage data. 
The analysis includes price trends, technical indicators, and key metrics to assist in investment decisions.

\subsection{Key Metrics Overview}

\begin{longtable}{|l|c|c|c|c|c|}
\hline
\textbf{Symbol} & \textbf{Price} & \textbf{RSI} & \textbf{Trend} & \textbf{Volume} & \textbf{Volatility} \\
\hline
"""
        
        for data in report_data:
            summary = data['summary']
            symbol = data['symbol']
            
            # Determine trend color
            if summary['is_bullish']:
                trend_color = r'\textcolor{bullish}{Bullish}'
            elif summary['is_bearish']:
                trend_color = r'\textcolor{bearish}{Bearish}'
            else:
                trend_color = r'\textcolor{neutral}{Neutral}'
            
            content += f"""
{symbol} & \\${summary['current_price']} & {summary['rsi'] or 'N/A'} & {trend_color} & {summary['volume']:,} & {summary['volatility']:.4f} \\\\
\\hline
"""
        
        content += r"""
\end{longtable}

"""
        
        return content
    
    def _generate_stock_section(self, data, plots):
        """Generate individual stock analysis section"""
        symbol = data['symbol']
        summary = data['summary']
        technical_signals = data['technical_signals']
        price_levels = data['price_levels']
        
        content = f"""
\\section{{{symbol} Analysis}}

\\subsection{{Current Status}}

\\begin{{itemize}}
    \\item \\textbf{{Current Price:}} \\${summary['current_price']}
    \\item \\textbf{{Last Updated:}} {summary['last_updated']}
    \\item \\textbf{{Volume:}} {summary['volume']:,}
    \\item \\textbf{{Volatility:}} {summary['volatility']:.4f}
    \\item \\textbf{{Data Points:}} {summary['data_points']}
\\end{{itemize}}

\\subsection{{Technical Indicators}}

\\begin{{table}}[h]
\\centering
\\begin{{tabular}}{{|l|c|}}
\\hline
\\textbf{{Indicator}} & \\textbf{{Value}} \\\\
\\hline
"""
        
        # Add technical indicators
        if summary['rsi'] is not None:
            content += f"RSI (14) & {summary['rsi']:.1f} \\\\\n\\hline\n"
        if summary['macd'] is not None:
            content += f"MACD & {summary['macd']:.3f} \\\\\n\\hline\n"
        if summary['ma_50'] is not None:
            content += f"50-Day MA & \\${summary['ma_50']:.2f} \\\\\n\\hline\n"
        if summary['ma_200'] is not None:
            content += f"200-Day MA & \\${summary['ma_200']:.2f} \\\\\n\\hline\n"
        
        # Add price levels
        for level, value in price_levels.items():
            content += f"{level.title()} & \\${value} \\\\\n\\hline\n"
        
        content += r"""
\end{tabular}
\caption{""" + f"{symbol} Technical Indicators" + r"""}
\end{table}

\subsection{Technical Signals}

\begin{itemize}
"""
        
        # Add technical signals
        for signal, value in technical_signals.items():
            status = "✓" if value else "✗"
            signal_name = signal.replace('_', ' ').title()
            content += f"    \\item \\textbf{{{signal_name}:}} {status}\n"
        
        content += r"""
\end{itemize}

\subsection{Price Chart}

\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{""" + plots['price'] + r"""}
\caption{""" + f"{symbol} Price Chart with Moving Averages" + r"""}
\end{figure}

\subsection{Technical Analysis}

\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{""" + plots['technical'] + r"""}
\caption{""" + f"{symbol} Technical Indicators" + r"""}
\end{figure}

\subsection{Bollinger Bands}

\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{""" + plots['bollinger'] + r"""}
\caption{""" + f"{symbol} Bollinger Bands Analysis" + r"""}
\end{figure}

\subsection{Volume Analysis}

\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{""" + plots['volume'] + r"""}
\caption{""" + f"{symbol} Volume Analysis" + r"""}
\end{figure}

\newpage

"""
        
        return content
    
    def _generate_market_analysis(self, report_data):
        """Generate market analysis section for multiple stocks"""
        content = r"""
\section{Market Analysis}

\subsection{Comparative Analysis}

This section compares the performance and technical indicators across all analyzed stocks.

\begin{table}[h]
\centering
\begin{tabular}{|l|c|c|c|c|}
\hline
\textbf{Symbol} & \textbf{Bullish Signals} & \textbf{Bearish Signals} & \textbf{RSI} & \textbf{Recommendation} \\
\hline
"""
        
        for data in report_data:
            symbol = data['symbol']
            summary = data['summary']
            technical_signals = data['technical_signals']
            
            # Count signals
            bullish_count = sum(1 for v in technical_signals.values() if v and 'bullish' in str(v).lower())
            bearish_count = sum(1 for v in technical_signals.values() if v and 'bearish' in str(v).lower())
            
            # Generate recommendation
            if summary['is_bullish']:
                recommendation = r'\textcolor{bullish}{Buy}'
            elif summary['is_bearish']:
                recommendation = r'\textcolor{bearish}{Sell}'
            else:
                recommendation = r'\textcolor{neutral}{Hold}'
            
            content += f"""
{symbol} & {bullish_count} & {bearish_count} & {summary['rsi'] or 'N/A'} & {recommendation} \\\\
\\hline
"""
        
        content += r"""
\end{tabular}
\caption{Comparative Technical Analysis}
\end{table}

"""
        
        return content
    
    def _generate_conclusion(self, report_data):
        """Generate conclusion section"""
        content = r"""
\section{Conclusion and Recommendations}

Based on the technical analysis performed, here are the key findings:

\begin{itemize}
"""
        
        for data in report_data:
            symbol = data['symbol']
            summary = data['summary']
            
            if summary['is_bullish']:
                content += f"    \\item \\textbf{{{symbol}:}} Shows bullish momentum with positive technical indicators.\n"
            elif summary['is_bearish']:
                content += f"    \\item \\textbf{{{symbol}:}} Displays bearish signals requiring caution.\n"
            else:
                content += f"    \\item \\textbf{{{symbol}:}} Currently in a neutral trend with mixed signals.\n"
        
        content += r"""
\end{itemize}

\subsection{Risk Considerations}

\begin{itemize}
    \item Market volatility can impact technical analysis accuracy
    \item External factors (news, earnings) may override technical signals
    \item Always consider risk management and position sizing
    \item This analysis is for educational purposes only
\end{itemize}

\subsection{Data Source}

This report uses data from Alpha Vantage, a leading provider of financial market data. 
All technical indicators are calculated using standard formulas and industry best practices.

\textbf{Disclaimer:} This report is for informational purposes only and should not be considered as investment advice. 
Please consult with a qualified financial advisor before making investment decisions.

"""
        
        return content
    
    def _compile_latex(self, tex_file):
        """Compile LaTeX file to PDF"""
        try:
            # Check if pdflatex is available
            if not shutil.which('pdflatex'):
                print("Warning: pdflatex not found. Please install LaTeX to generate PDFs.")
                return tex_file
            
            # Compile LaTeX (run twice for proper references)
            for i in range(2):
                result = subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode',
                    '-output-directory', str(tex_file.parent),
                    str(tex_file)
                ], capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"LaTeX compilation error: {result.stderr}")
                    return tex_file
            
            # Clean up auxiliary files
            for ext in ['.aux', '.log', '.toc']:
                aux_file = tex_file.with_suffix(ext)
                if aux_file.exists():
                    aux_file.unlink()
            
            pdf_file = tex_file.with_suffix('.pdf')
            if pdf_file.exists():
                print(f"PDF generated successfully: {pdf_file}")
                return pdf_file
            else:
                print(f"PDF generation failed")
                return tex_file
                
        except Exception as e:
            print(f"Error compiling LaTeX: {e}")
            return tex_file
    
    def _open_pdf(self, pdf_path):
        """Auto-open PDF file on macOS"""
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(["open", str(pdf_path)], check=True)
                print(f"📖 Opened PDF: {pdf_path}")
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", str(pdf_path)], check=True)
                print(f"📖 Opened PDF: {pdf_path}")
            elif sys.platform == "win32":
                os.startfile(str(pdf_path))
                print(f"📖 Opened PDF: {pdf_path}")
            else:
                print(f"📄 PDF generated: {pdf_path}")
        except Exception as e:
            print(f"⚠️ Could not auto-open PDF: {e}")
            print(f"📄 PDF generated: {pdf_path}")
    
    def generate_json_report(self, symbols):
        """Generate JSON report (for API compatibility)"""
        report_data = self._collect_stock_data(symbols)
        
        json_report = {
            'generated_at': datetime.now().isoformat(),
            'symbols': symbols,
            'stocks': []
        }
        
        for data in report_data:
            stock_data = {
                'symbol': data['symbol'],
                'summary': data['summary'],
                'technical_signals': data['technical_signals'],
                'price_levels': data['price_levels']
            }
            json_report['stocks'].append(stock_data)
        
        return json_report


def main():
    """CLI interface for report generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate LaTeX stock analysis reports')
    parser.add_argument('symbols', nargs='*', default=FAVORITE_STOCKS, help='Stock symbols to analyze')
    parser.add_argument('--type', choices=['comprehensive', 'summary', 'technical'], 
                       default='comprehensive', help='Report type')
    parser.add_argument('--output', '-o', default='latex_reports', 
                       help='Output directory')
    
    args = parser.parse_args()
    
    # Generate report
    generator = LatexReportGenerator(args.output)
    pdf_path, message = generator.generate_report(args.symbols or FAVORITE_STOCKS, args.type)
    
    print(f"Report generation: {message}")
    if pdf_path:
        print(f"Report saved to: {pdf_path}")


if __name__ == "__main__":
    main()
