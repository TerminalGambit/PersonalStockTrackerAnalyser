from signal_detector import SignalDetector

ticker = "AAPL"
detector = SignalDetector(ticker)
signals = detector.analyze()

import pandas as pd
import matplotlib.pyplot as plt

print("\n📊 Indicator Status:")
print(f"RSI: {round(detector.stock.get_rsi().iloc[-1], 2)}")
print(f"MACD: {round(detector.stock.get_macd().iloc[-1], 2)}")
upper, lower = detector.stock.get_bollinger_bands()
print(f"Price: {detector.stock.history['Close'].iloc[-1]}")
print(f"Bollinger Upper: {round(upper.iloc[-1], 2)}")
print(f"Bollinger Lower: {round(lower.iloc[-1], 2)}\n")

if not signals:
    print(f"📭 No signals for {ticker} at this time.")
else:
    print(f"📊 Signals for {ticker}:")
    for signal in signals:
        print(f"🔔 {signal['indicator']} suggests a {signal['signal']} (value: {signal['value']})")

# Always visualize the price and bands
plt.figure(figsize=(14, 6))
plt.plot(detector.stock.history["Close"], label="Close Price")
plt.plot(upper, linestyle="--", label="Upper Bollinger")
plt.plot(lower, linestyle="--", label="Lower Bollinger")

if signals:
    last_price = detector.stock.history["Close"].iloc[-1]
    for signal in signals:
        plt.axhline(y=last_price, linestyle=":", color="green" if signal["signal"] == "buy" else "red", alpha=0.5)

plt.title(f"{ticker} Signal Chart")
plt.legend()
plt.tight_layout()
plt.show()