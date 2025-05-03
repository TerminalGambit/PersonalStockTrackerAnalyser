import pandas as pd
from stock import Stock


class SignalDetector:
    def __init__(self, ticker, rsi_low=30, rsi_high=70):
        self.ticker = ticker
        self.stock = Stock(ticker)
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high
        self._history = self.stock.history

    def analyze(self):
        latest_price = self._history['Close'].iloc[-1]
        rsi_value = self.stock.get_rsi().iloc[-1]
        macd_series = self.stock.get_macd()
        upper_band, lower_band = self.stock.get_bollinger_bands()
        upper_value = upper_band.iloc[-1]
        lower_value = lower_band.iloc[-1]

        signals = []

        # RSI Signal
        if rsi_value < self.rsi_low:
            signals.append({
                "indicator": "RSI",
                "signal": "buy",
                "value": round(rsi_value, 2)
            })
        elif rsi_value > self.rsi_high:
            signals.append({
                "indicator": "RSI",
                "signal": "sell",
                "value": round(rsi_value, 2)
            })

        # MACD Signal
        if len(macd_series) >= 2:
            prev_macd = macd_series.iloc[-2]
            curr_macd = macd_series.iloc[-1]
            if curr_macd > 0 and prev_macd < 0:
                signals.append({
                    "indicator": "MACD",
                    "signal": "buy",
                    "value": round(curr_macd, 2)
                })
            elif curr_macd < 0 and prev_macd > 0:
                signals.append({
                    "indicator": "MACD",
                    "signal": "sell",
                    "value": round(curr_macd, 2)
                })

        # Bollinger Bands Signal
        if latest_price < lower_value:
            signals.append({
                "indicator": "Bollinger Bands",
                "signal": "buy",
                "value": round(latest_price, 2)
            })
        elif latest_price > upper_value:
            signals.append({
                "indicator": "Bollinger Bands",
                "signal": "sell",
                "value": round(latest_price, 2)
            })

        return signals

    def to_dataframe(self):
        """Return signals as a DataFrame for export or analysis."""
        return pd.DataFrame(self.analyze())