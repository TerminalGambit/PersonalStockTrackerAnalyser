import os
from stock import Stock
import matplotlib.pyplot as plt
from datetime import datetime


def generate_latex_report(ticker, period="1y"):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = f"latex_reports/{ticker}_{timestamp}"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "report.tex")

    stock = Stock(ticker, period=period)

    today_data = stock.today()
    growth = stock.get_growth()
    volatility = stock.volatility()
    pe_ratio = stock.info.get("trailingPE", "N/A")
    market_cap = stock.info.get("marketCap", "N/A")
    price = stock.history["Close"].iloc[-1]

    # Export history with indicators
    stock.history.to_csv(os.path.join(output_dir, f"{ticker}_history.csv"))

    start_date = stock.history.index.min().strftime("%Y-%m-%d")
    end_date = stock.history.index.max().strftime("%Y-%m-%d")

    def format_large_number(n):
        if isinstance(n, (int, float)):
            if n >= 1e12:
                return f"{n / 1e12:.2f} Trillion"
            elif n >= 1e9:
                return f"{n / 1e9:.2f} Billion"
            elif n >= 1e6:
                return f"{n / 1e6:.2f} Million"
            else:
                return f"{n:,.2f}"
        return n

    df = stock.history

    # Bollinger Bands plot
    bb_fig_path = os.path.join(
        output_dir, f"bollinger_{ticker}_{timestamp}.png")
    plt.figure(figsize=(10, 5))
    plt.plot(df["Close"], label="Close")
    plt.plot(df["Upper Band"], label="Upper Band", linestyle="--")
    plt.plot(df["Lower Band"], label="Lower Band", linestyle="--")
    plt.fill_between(df.index, df["Lower Band"], df["Upper Band"], alpha=0.1)
    plt.title(f"{ticker} Bollinger Bands")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    plt.savefig(bb_fig_path)
    plt.close()

    # MACD plot
    macd_path = os.path.join(output_dir, f"macd_{ticker}_{timestamp}.png")
    plt.figure(figsize=(10, 4))
    plt.plot(df["MACD"], label="MACD", color="b")
    plt.plot(df["Signal"], label="Signal Line", color="orange")
    plt.bar(df.index, df["Histogram"],
            label="Histogram", color="gray", alpha=0.3)
    plt.title(f"{ticker} MACD")
    plt.legend()
    plt.tight_layout()
    plt.savefig(macd_path)
    plt.close()

    # RSI plot
    rsi_path = os.path.join(output_dir, f"rsi_{ticker}_{timestamp}.png")
    plt.figure(figsize=(10, 3))
    plt.plot(df["RSI"], label="RSI", color="purple")
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title(f"{ticker} RSI")
    plt.tight_layout()
    plt.savefig(rsi_path)
    plt.close()

    # Format today's data
    today_table = "\\begin{tabular}{lr}\\textbf{Metric} & \\textbf{Value} \\\\\n\\hline\n"
    for col, val in today_data.items():
        if isinstance(val, float):
            val = f"{val:,.2f}"
        today_table += f"{col} & {val} \\\\\n"
    today_table += "\\end{tabular}"

    latex_content = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\title{Stock Report: %(ticker)s}
\author{Jack Massey}
\date{\today}

\begin{document}
\maketitle

\section*{Summary}
\textbf{Period:} %(start_date)s to %(end_date)s

\begin{itemize}
    \item Latest Close Price: %(price).2f USD
    \item Growth (1Y): %(growth).2f\%%
    \item Volatility: %(volatility).4f
    \item P/E Ratio: %(pe_ratio)s
    \item Market Cap: %(market_cap)s
\end{itemize}

\section*{Today's Data}
%(today_table)s

\section*{Bollinger Bands}
\includegraphics[width=\textwidth]{%(bb_plot)s}

\textit{Close is between upper and lower bands, possibly indicating consolidation or pending breakout.}

\section*{MACD}
\includegraphics[width=\textwidth]{%(macd_plot)s}

\textit{Look for signal line crossovers to identify bullish or bearish shifts in momentum.}

\section*{RSI}
\includegraphics[width=\textwidth]{%(rsi_plot)s}

\textit{RSI near 70 indicates overbought; near 30 suggests oversold.}

\section*{Insights}
%(ticker)s shows recent volatility trends with Bollinger Bands and momentum signals through MACD and RSI. Review context in relation to market news or events.

\end{document}
""" % {
        "ticker": ticker,
        "price": price,
        "growth": growth,
        "volatility": volatility,
        "pe_ratio": f"{pe_ratio:.2f}" if isinstance(pe_ratio, (float, int)) else pe_ratio,
        "market_cap": format_large_number(market_cap),
        "today_table": today_table,
        "start_date": start_date,
        "end_date": end_date,
        "bb_plot": os.path.basename(bb_fig_path),
        "macd_plot": os.path.basename(macd_path),
        "rsi_plot": os.path.basename(rsi_path)
    }

    with open(output_path, "w") as f:
        f.write(latex_content)
    print(f"LaTeX report generated at {output_path}")

    os.system(
        f"pdflatex -interaction=nonstopmode -output-directory={output_dir} {output_path}")


if __name__ == "__main__":
    generate_latex_report("AAPL", period="1y")
