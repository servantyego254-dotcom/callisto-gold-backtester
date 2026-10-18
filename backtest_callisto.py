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

# 2. ACTIVE TRADING STRATEGY (Guaranteed Trade Execution)
class CallistoActiveTrader(Strategy):
    def init(self):
        # Simple momentum indicator
        self.sma = self.I(lambda x: pd.Series(x).rolling(5).mean(), self.data.Close)

    def next(self):
        if not self.position:
            # Enter trades based on price momentum relative to SMA
            if self.data.Close[-1] > self.sma[-1]:
                self.buy(sl=self.data.Close[-1] - 4.0, tp=self.data.Close[-1] + 8.0)
            else:
                self.sell(sl=self.data.Close[-1] + 4.0, tp=self.data.Close[-1] - 8.0)

# 3. RUN BACKTEST
bt = Backtest(
    data, 
    CallistoActiveTrader, 
    cash=1000, 
    commission=0.0002, 
    exclusive_orders=True
)

stats = bt.run()
print("\n=== CALLISTOFX BACKTEST RESULTS ===")
print(stats)
