import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# ==========================================
# 1. FETCH HISTORICAL 5-MINUTE GOLD DATA
# ==========================================
def get_gold_data():
    # Fetch 5-minute Gold data for the last month
    df = yf.download(tickers="GC=F", period="1mo", interval="5m")
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df = df.rename(columns={
        "Open": "Open",
        "High": "High",
        "Low": "Low",
        "Close": "Close",
        "Volume": "Volume"
    })
    return df.dropna()

# ==========================================
# 2. CALLISTOFX DYNAMIC T.R.C. MODEL
# ==========================================
class CallistoTRC(Strategy):
    tp_pips = 2.0      # +20 Pips in Gold ($2.00 move)
    sl_pips = 1.5      # $1.50 Stop Loss
    lookback = 10      # 10-bar swing high/low lookback for CHoCH
    
    def init(self):
        # Rolling swing highs and lows for 5M structure break
        self.swing_high = self.I(lambda x: pd.Series(x).rolling(self.lookback).max(), self.data.High)
        self.swing_low = self.I(lambda x: pd.Series(x).rolling(self.lookback).min(), self.data.Low)

    def next(self):
        close_price = self.data.Close[-1]
        
        # BUY ENTRY: 5M Body Close above recent swing high
        if not self.position:
            if close_price > self.swing_high[-2]: 
                sl = close_price - self.sl_pips
                tp = close_price + self.tp_pips
                self.buy(sl=sl, tp=tp)
                
            # SELL ENTRY: 5M Body Close below recent swing low
            elif close_price < self.swing_low[-2]: 
                sl = close_price + self.sl_pips
                tp = close_price - self.tp_pips
                self.sell(sl=sl, tp=tp)

# ==========================================
# 3. BACKTEST EXECUTION
# ==========================================
if __name__ == "__main__":
    data = get_gold_data()
    
    bt = Backtest(
        data, 
        CallistoTRC, 
        cash=1000, 
        commission=0.0002, 
        exclusive_orders=True
    )
    
    stats = bt.run()
    print("\n--- CALLISTOFX 5M BACKTEST RESULTS ---")
    print(stats)
    
