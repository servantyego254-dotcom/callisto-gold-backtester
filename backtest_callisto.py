import pandas as pd
import numpy as np
import yfinance as yf
from backtesting import Backtest, Strategy

# ==========================================
# 1. FETCH HISTORICAL GOLD DATA (XAUUSD)
# ==========================================
def get_gold_data():
    # Downloads 1-hour Gold historical data from Yahoo Finance
    df = yf.download(tickers="GC=F", period="60d", interval="1h")
    
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
# 2. CALLISTOFX T.R.C. STRATEGY MODEL
# ==========================================
class CallistoTRC(Strategy):
    tp_pips = 2.0      # +20 Pips in Gold ($2.00 move)
    sl_pips = 1.5      # $1.50 Stop Loss
    
    def init(self):
        # Moving averages representing Higher Timeframe Trend Bias
        self.fast_ma = self.I(lambda x: pd.Series(x).rolling(10).mean(), self.data.Close)
        self.slow_ma = self.I(lambda x: pd.Series(x).rolling(30).mean(), self.data.Close)

    def next(self):
        bullish_bias = self.fast_ma[-1] > self.slow_ma[-1]
        bearish_bias = self.fast_ma[-1] < self.slow_ma[-1]
        
        close_price = self.data.Close[-1]
        
        # BUY ENTRY: Bullish trend + Strong breakout candle
        if bullish_bias and not self.position:
            if close_price > self.data.High[-2]: 
                sl = close_price - self.sl_pips
                tp = close_price + self.tp_pips
                self.buy(sl=sl, tp=tp)
                
        # SELL ENTRY: Bearish trend + Strong breakdown candle
        elif bearish_bias and not self.position:
            if close_price < self.data.Low[-2]: 
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
    print("\n--- CALLISTOFX BACKTEST RESULTS ---")
    print(stats)
              
