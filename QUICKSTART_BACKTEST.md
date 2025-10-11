# 🚀 QUICK START - Backtest Your Trading Signals

## Run in 3 Simple Steps

### Step 1: Open Terminal
```bash
cd "c:\Users\admin\Documents\JOB APP\FastAPI\gitpullTradesignalold\TradeSignal"
```

### Step 2: Run Backtest
```bash
run_backtest.bat
```

### Step 3: Review Results
Open these files to see results:
- `backtest_results.json` - Daily signals with reasons
- `backtest_transactions.json` - All trades executed
- `backtest_metrics.json` - Performance summary

---

## What It Does

Tests your trading signals from **September 3 - October 3, 2025**:

1. **Generates signals** for each day using only past data (no cheating)
2. **Executes trades** based on signals with $1,000 starting capital
3. **Shows detailed reasons** for every signal (why buy? why sell?)
4. **Calculates performance** (profit/loss, win rate, etc.)
5. **Compares to buy-and-hold** (did your signals beat just holding?)

---

## Example Output

```
📅 2025-09-03 | $282.16 | WEAK_BUY (62%) | BUY 3 shares
   💡 RSI Oversold (28.3) | MACD Bullish | Price above 200 SMA

📅 2025-09-10 | $290.45 | SELL (78%) | SELL 3 shares (Profit: +2.94%)
   💡 RSI Overbought (72.1) | Death Cross | High volume confirms

Final Result: $1,045.23 (+4.52%)
Buy-and-Hold: $1,021.35 (+2.13%)
You OUTPERFORMED by +2.39%! ✅
```

---

## Key Features

✅ **Detailed Explanations** - See exactly why each signal was generated  
✅ **No Look-Ahead Bias** - Uses only data available at that time  
✅ **Realistic Trading** - Follows same logic as your website  
✅ **Performance Metrics** - Win rate, max drawdown, total return  
✅ **Benchmark Comparison** - Beat buy-and-hold?  
✅ **Website-Safe** - Completely separate, won't affect your site  

---

## That's It!

Just run `run_backtest.bat` and watch your signals get tested! 🎯
