import json

def load_glossary(file_path="glossary.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_glossary(glossary, file_path="glossary.json"):
    with open(file_path, "w") as f:
        json.dump(glossary, f, indent=4)

def add_term(term, definition, file_path="glossary.json"):
    glossary = load_glossary(file_path)
    glossary[term] = definition
    save_glossary(glossary, file_path)

def generate_markdown(file_path="glossary.json", output_path="glossary.md"):
    glossary = load_glossary(file_path)
    with open(output_path, "w") as f:
        f.write("# 📘 Finance Glossary\n\n")
        for term in sorted(glossary):
            f.write(f"## {term}\n")
            f.write(f"{glossary[term]}\n\n")

if __name__ == "__main__":
    # Example usage:
    add_term("P/E Ratio", "Price-to-Earnings ratio: stock price divided by earnings per share.")
    add_term("Dividend", "A payout to shareholders from the company's profits.")
    add_term("Market Capitalization", "Total value of a company's outstanding shares; calculated as share price × number of shares.")
    add_term("Beta", "A measure of a stock's volatility compared to the overall market; beta > 1 means more volatile.")
    add_term("Volume", "The number of shares traded during a specific period.")
    add_term("Moving Average", "An average of stock prices over a period to smooth out short-term fluctuations.")
    add_term("RSI", "Relative Strength Index: a momentum indicator measuring the magnitude of recent price changes.")
    add_term("MACD", "Moving Average Convergence Divergence: a trend-following momentum indicator.")
    add_term("Volatility", "Statistical measure of the dispersion of returns; often measured using standard deviation.")
    add_term("Earnings Per Share", "A company's net profit divided by the number of outstanding shares.")
    generate_markdown()
    print("Glossary updated and Markdown generated.")
