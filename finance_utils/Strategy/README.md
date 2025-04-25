
# Strategy Module Design

This directory will contain reusable investment strategy logic for the portfolio simulation system.

## Goal

The objective is to create modular strategies that can interpret stock indicators (e.g., RSI, MACD, Bollinger Bands) and decide whether to buy, sell, or hold. Each strategy can be independently tested, tuned, and combined.

## Architecture

- `BaseStrategy`: An abstract class/interface that defines:
  - `should_buy(stock: Stock) -> bool`
  - `should_sell(stock: Stock) -> bool`
  - Optional: `score(stock: Stock) -> float` for ranking

- Concrete implementations:
  - `RSIStrategy`: Buy low RSI, sell high RSI
  - `MACDStrategy`: Uses MACD crossovers to determine action
  - `BollingerBreakoutStrategy`: Buys when price hits lower band, sells upper
  - `CombinedStrategy`: Composes several strategies and assigns weights

## Integration

The `Portfolio` class will support a method like `apply_strategy(strategy: BaseStrategy)` that simulates portfolio actions across all stocks.

## Example Strategy Logic

```python
class RSIStrategy(BaseStrategy):
    def should_buy(self, stock):
        return stock.latest_data["RSI"] < 30

    def should_sell(self, stock):
        return stock.latest_data["RSI"] > 70
```

## To Do

- [ ] Implement `BaseStrategy`
- [ ] Create RSI, MACD, and Bollinger strategies
- [ ] Add unit tests
- [ ] Allow strategy simulation over time
- [ ] Visualize strategy performance