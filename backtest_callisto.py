# 1. INSTALL LIBRARIES
!pip install pandas numpy backtesting yfinance

import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# 2. DOWNLOAD GOLD DATA
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

# 3. TRADING STRATEGY
class CallistoActiveTrader(Strategy):
    def init(self):
        self.ma_fast = self.I(lambda x: pd.Series(x).rolling(6).mean(), self.data.Close)
        self.ma_slow = self.I(lambda x: pd.Series(x).rolling(18).mean(), self.data.Close)

    def next(self):
        if not self.position:
            if self.ma_fast[-1] > self.ma_slow[-1]:
                self.buy(sl=self.data.Close[-1] - 5.0, tp=self.data.Close[-1] + 10.0)
            elif self.ma_fast[-1] < self.ma_slow[-1]:
                self.sell(sl=self.data.Close[-1] + 5.0, tp=self.data.Close[-1] - 10.0)

# 4. RUN BACKTEST
bt = Backtest(
    data, 
    CallistoActiveTrader, 
    cash=1000, 
    commission=0.0002, 
    exclusive_orders=True
)

stats = bt.run()
print("\n=== BACKTEST RESULTS ===")
print(stats)
