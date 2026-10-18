import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# 1. DOWNLOAD GOLD DATA
print("Downloading Gold Data...")
data = yf.download(tickers="GC=F", period="1mo", interval="1h")

if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data = data.rename(columns={
    "Open": "Open",
    "High": "High",
    "Low": "Low",
    "Close": "Close",
    "Volume": "Volume"
}).dropna()

# 2. GUARANTEED EXECUTION STRATEGY (No indicators to fail)
class CallistoGuaranteed(Strategy):
    def next(self):
        if not self.position:
            # Buy if candle is green, Sell if candle is red
            if self.data.Close[-1] > self.data.Open[-1]:
                self.buy(sl=self.data.Close[-1] - 5.0, tp=self.data.Close[-1] + 10.0)
            else:
                self.sell(sl=self.data.Close[-1] + 5.0, tp=self.data.Close[-1] - 10.0)

# 3. RUN BACKTEST
bt = Backtest(
    data, 
    CallistoGuaranteed, 
    cash=1000, 
    commission=0.0002, 
    exclusive_orders=True
)

stats = bt.run()
print("\n=== FINAL BACKTEST RESULTS ===")
print(stats)
