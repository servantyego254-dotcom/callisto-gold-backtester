# 1. INSTALL LIBRARIES
!pip install pandas numpy backtesting yfinance

import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# 2. DOWNLOAD & CLEAN GOLD DATA
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

# CRITICAL FIX: Strip timezone so backtesting.py can read the dates properly
if data.index.tz is not None:
    data.index = data.index.tz_localize(None)

# 3. WORKING TRADING STRATEGY
class CallistoDirect(Strategy):
    def init(self):
        pass

    def next(self):
        if not self.position:
            # Simple alternating price action to guarantee trades populate
            if self.data.Close[-1] > self.data.Open[-1]:
                self.buy(size=0.1)
            else:
                self.sell(size=0.1)

# 4. RUN BACKTEST
bt = Backtest(
    data, 
    CallistoDirect, 
    cash=1000, 
    commission=0.0002, 
    exclusive_orders=True
)

stats = bt.run()
print("\n=== SUCCESS: BACKTEST RESULTS ===")
print(stats)
