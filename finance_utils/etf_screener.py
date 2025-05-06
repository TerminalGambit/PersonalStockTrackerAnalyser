from twelvedata import TDClient
from dotenv import load_dotenv
import os
import pandas as pd
import time
import logging

load_dotenv()
API_KEY = os.getenv("API_KEY")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class ETFScreener:
    def __init__(self, tickers):
        self.tickers = tickers
        self.etf_data = []
        self.df = pd.DataFrame()

    def _wait_if_needed(self, index):
        if (index + 1) % 8 == 0 and (index + 1) < len(self.tickers):
            logging.info("⏳ Waiting 60 seconds to avoid API rate limit...")
            time.sleep(60)
        else:
            time.sleep(1)

    def fetch_data(self, max_retries=3):
        client = TDClient(apikey=API_KEY)
        self.etf_data = []

        for i, ticker in enumerate(self.tickers):
            retries = 0
            while retries < max_retries:
                try:
                    logging.info(f"Fetching data for {ticker}")
                    response = client.time_series(symbol=ticker, interval="1day", outputsize=1).as_json()
                    if "values" in response and response["values"]:
                        price = float(response["values"][0].get("close", "nan"))
                        self.etf_data.append({"Ticker": ticker, "Price": price})
                    else:
                        raise ValueError("Unexpected API response structure")
                    break
                except Exception as e:
                    logging.warning(f"Attempt {retries + 1} failed for {ticker}: {e}")
                    retries += 1
                    time.sleep(2 ** retries)

            if retries == max_retries:
                logging.error(f"Failed to fetch {ticker} after {max_retries} attempts.")

            self._wait_if_needed(i)

        self.df = pd.DataFrame(self.etf_data)

    def filter_by(self, **kwargs):
        if self.df.empty:
            logging.warning("No data to filter.")
            return pd.DataFrame()
        df = self.df.copy()
        for key, value in kwargs.items():
            if key not in df.columns:
                logging.warning(f"Column '{key}' not found in data.")
                continue
            if isinstance(value, tuple) and len(value) == 2:
                df = df[df[key].between(value[0], value[1])]
            else:
                df = df[df[key] == value]
        return df

    def top_n_by(self, column, n=5, ascending=True):
        if self.df.empty:
            logging.warning("No data available.")
            return pd.DataFrame()
        if column not in self.df.columns:
            logging.warning(f"Column '{column}' not found in DataFrame.")
            return pd.DataFrame()
        return self.df.sort_values(by=column, ascending=ascending).head(n)

    def describe(self):
        return self.df.describe(include='all') if not self.df.empty else pd.DataFrame()

    def export_to_csv(self, filename="etf_screener_output.csv"):
        if not self.df.empty:
            self.df.to_csv(filename, index=False)
            logging.info(f"Exported data to {filename}")
        else:
            logging.warning("No data to export.")

# Example usage:
if __name__ == "__main__":
    tickers = ["SPY", "QQQ", "VTI", "DIA", "ARKK", "XLK", "XLF", "XLE", "IWM", "EFA"]
    screener = ETFScreener(tickers)
    screener.fetch_data()

    if not screener.df.empty:
        if "ExpenseRatio" in screener.df.columns:
            print("Top 5 ETFs with lowest Expense Ratios:")
            print(screener.top_n_by("ExpenseRatio", ascending=True))
    else:
        print("⚠️ No data fetched. Try again later.")
