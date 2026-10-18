import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# 1. DOWNLOAD GOLD (XAUUSD) 5-MINUTE DATA
print("Downloading 5M Gold Data...")
data = yf.download(tickers="GC=F", period="5d", interval="5m")

# Clean up DataFrame columns
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.get_level_values(0)

data = data.rename(columns={
    "Open": "Open",
    "High": "High",
    "Low": "Low",
    "Close": "Close",
    "Volume": "Volume"
}).dropna()

# 2. DEFINE CALLISTOFX STRATEGY MODEL
class CallistoTRC(Strategy):
    tp_pips = 1.5      # Take Profit ($1.50 Gold move)
    sl_pips = 1.0      # Stop Loss ($1.00 Gold move)
    lookback = 5       # 5-bar swing high/low for 5M CHoCH

    def init(self):
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(self.lookback).max(), self.data.High)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(self.lookback).min(), self.data.Low)

    def next(self):
        close_price = self.data.Close[-1]
        
        # BUY: Price breaks above recent 5-bar high
        if not self.position:
            if close_price > self.swing_high[-2]: 
                self.buy(sl=close_price - self.sl_pips, tp=close_price + self.tp_pips)
                
            # SELL: Price breaks below recent 5-bar low
            elif close_price < self.swing_low[-2]: 
                self.sell(sl=close_price + self.sl_pips, tp=close_price - self.tp_pips)

# 3. RUN BACKTEST
bt = Backtest(
    data, 
    CallistoTRC, 
    cash=1000, 
    commission=0.0002, 
    exclusive_orders=True
)

stats = bt.run()
print("\n=== CALLISTOFX BACKTEST RESULTS ===")
print(stats)
