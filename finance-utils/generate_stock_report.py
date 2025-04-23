import os
from finance_utils import Stock

def generate_latex_report(ticker, output_path="latex_output/report.tex"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    stock = Stock(ticker)

    # Collect data
    today_data = stock.today()
    growth = stock.get_growth()
    volatility = stock.volatility()
    pe_ratio = stock.info.get("trailingPE", "N/A")
    market_cap = stock.info.get("marketCap", "N/A")
    price = stock.history["Close"].iloc[-1]

    # LaTeX content
    latex_content = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage[margin=1in]{geometry}
\title{Stock Report: %(ticker)s}
\date{}

\begin{document}
\maketitle

\section*{Summary}
\begin{itemize}
    \item Latest Close Price: %(price).2f USD
    \item Growth (1Y): %(growth).2f\%%
    \item Volatility: %(volatility).4f
    \item P/E Ratio: %(pe_ratio)s
    \item Market Cap: %(market_cap)s
\end{itemize}

\section*{Today's Data}
\begin{verbatim}
%(today_data)s
\end{verbatim}

\end{document}
""" % {
        "ticker": ticker,
        "price": price,
        "growth": growth,
        "volatility": volatility,
        "pe_ratio": pe_ratio,
        "market_cap": market_cap,
        "today_data": today_data.to_string()
    }

    # Write to file
    with open(output_path, "w") as f:
        f.write(latex_content)
    print(f"LaTeX report generated at {output_path}")

    # Compile to PDF
    os.system(f"pdflatex -interaction=nonstopmode -output-directory={os.path.dirname(output_path)} {output_path}")

if __name__ == "__main__":
    generate_latex_report("AAPL")
