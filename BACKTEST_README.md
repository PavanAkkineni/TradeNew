# 📊 Trading Signal Backtesting System

## Overview

This backtesting system tests the **credibility and profitability** of your trading signals by simulating real trades over a historical period (September 3 - October 3, 2024) with **$1,000 initial capital**.

**Key Feature**: The backtest uses **NO LOOK-AHEAD BIAS** - signals are generated using only data available up to that specific date, exactly as they would have been in real-time.

---

## 🎯 What It Does

### Step 1: Signal Generation (`backtest_signals.py`)
For **each trading day** from Sept 3 to Oct 3:
1. Loads price data **only up to that date** (prevents future peeking)
2. Calculates technical indicators (RSI, MACD, Moving Averages, Bollinger Bands, Volume)
3. Evaluates fundamental metrics (P/E, ROE, Margins, Debt/Equity)
4. Assesses sentiment data
5. Generates comprehensive trade signal: **STRONG_BUY, BUY, WEAK_BUY, HOLD, WEAK_SELL, SELL, STRONG_SELL**
6. Provides **detailed explanation** with specific reasons for the signal
7. Calculates confidence level and risk assessment

### Step 2: Trade Execution (`analyze_backtest_performance.py`)
1. Simulates actual trades based on generated signals
2. Starts with $1,000 cash
3. Executes buys/sells according to signal strength
4. Tracks portfolio value daily
5. Calculates:
   - Total return ($ and %)
   - Win rate
   - Maximum drawdown
   - Number of trades
   - Comparison to buy-and-hold strategy

---

## 🚀 How to Run

### Quick Start (Windows)
Simply double-click:
```
run_backtest.bat
```

### Manual Execution
```bash
# Step 1: Generate signals
python backtest_signals.py

# Step 2: Analyze performance
python analyze_backtest_performance.py
```

---

## 📋 Trading Strategy Rules

The backtest follows these rules (same as your website logic):

| Signal | Action | Condition |
|--------|--------|-----------|
| **STRONG_BUY** | Buy all available cash | High confidence bullish signal (score ≥ 35) |
| **BUY** | Buy all available cash | Bullish signal (score ≥ 20) |
| **WEAK_BUY** | Buy if no position | Mild bullish signal (score ≥ 10) |
| **HOLD** | No action | Neutral signal (-10 < score < 10) |
| **WEAK_SELL** | Sell only if losing 2%+ | Mild bearish signal (score ≤ -10) |
| **SELL** | Sell entire position | Bearish signal (score ≤ -20) |
| **STRONG_SELL** | Sell entire position immediately | Strong bearish signal (score ≤ -35) |

---

## 📊 Signal Scoring System

### Technical Analysis (Max ±65 points)
- **RSI** (±15 points): Oversold/overbought conditions
- **MACD** (±15 points): Momentum and crossovers
- **Moving Averages** (±20 points): Golden/Death cross, trend direction
- **Bollinger Bands** (±10 points): Price extremes
- **Volume** (±5 points): Confirmation of moves

### Fundamental Analysis (Max ±15 points, weighted 0.5x)
- **P/E Ratio** (±5): Valuation assessment
- **ROE** (±5): Management quality
- **Profit Margins** (±3): Profitability strength
- **Debt/Equity** (±2): Financial health

### Sentiment Analysis (Max ±10 points, weighted 0.5x)
- **Overall Sentiment**: Market mood and news analysis

**Total Score = Technical + (Fundamental × 0.5) + (Sentiment × 0.5)**

---

## 📁 Output Files

After running the backtest, you'll get these files:

### 1. `backtest_results.json`
Daily signals with complete breakdown:
```json
{
  "date": "2024-09-03",
  "price": 189.45,
  "signal": "WEAK_BUY",
  "confidence": 62,
  "risk_level": "MEDIUM",
  "total_score": 23.5,
  "technical_score": 35,
  "fundamental_score": 15,
  "sentiment_score": 22,
  "reasons": {
    "technical": [
      "✅ RSI Oversold (28.3) - Strong buy signal",
      "✅ MACD Bullish Crossover - Strong momentum",
      "✅ Price above 200 SMA - Bullish trend"
    ],
    "fundamental": [
      "✅ ROE (22.7%) - Excellent returns",
      "➖ P/E Ratio (46.3) - Fair value"
    ],
    "sentiment": [
      "➖ Neutral sentiment (0.05)"
    ]
  }
}
```

### 2. `backtest_transactions.json`
Complete transaction log:
```json
{
  "date": "2024-09-03",
  "action": "BUY",
  "signal": "WEAK_BUY",
  "shares": 5,
  "price": 189.45,
  "cost": 947.25,
  "commission": 0,
  "total_cost": 947.25,
  "cash_after": 52.75,
  "shares_after": 5,
  "reason": "Weak bullish signal. RSI Oversold | MACD Bullish"
}
```

### 3. `backtest_daily_values.json`
Portfolio value tracking:
```json
{
  "date": "2024-09-03",
  "price": 189.45,
  "cash": 52.75,
  "shares": 5,
  "stock_value": 947.25,
  "total_value": 1000.00,
  "return_pct": 0.00
}
```

### 4. `backtest_metrics.json`
Performance summary:
```json
{
  "total_return": 45.23,
  "total_return_pct": 4.52,
  "win_rate": 66.7,
  "max_drawdown": -3.45,
  "num_trades": 8,
  "buy_hold_return": 2.13,
  "outperformance": 2.39
}
```

---

## 📈 Example Output

```
================================================================================
TRADING SIGNAL BACKTEST
================================================================================
Symbol: IBM
Period: 2024-09-03 to 2024-10-03
Initial Capital: $1,000.00
Strategy: Follow daily trade signals
================================================================================

📊 Found 22 trading days in backtest period

📅 2024-09-03 | Price: $189.45 | Signal: WEAK_BUY | Confidence: 62% | Score: 23.5
   Technical: 35.0 | Fundamental: 15.0 | Sentiment: 22.0

📅 2024-09-04 | Price: $191.23 | Signal: BUY | Confidence: 75% | Score: 28.3
   Technical: 42.0 | Fundamental: 12.0 | Sentiment: 18.5

...

================================================================================
EXECUTING TRADES BASED ON SIGNALS
================================================================================

📅 2024-09-03 | $189.45 | WEAK_BUY (62%) | BUY 5 shares | Value: $1,000.00 (+0.00%)
   💡 Reason: Weak bullish signal. RSI Oversold (28.3) | MACD Bullish Crossover

📅 2024-09-10 | $195.67 | SELL (78%) | SELL 5 shares (P/L: +3.28%) | Value: $1,032.85 (+3.29%)
   💡 Reason: Strong bearish signal. RSI Overbought (72.1) | Death Cross forming

...

================================================================================
PERFORMANCE ANALYSIS
================================================================================

📊 SUMMARY STATISTICS:
--------------------------------------------------------------------------------
Initial Capital:        $1,000.00
Final Value:            $1,045.23
Total Return:           $45.23 (+4.52%)
Max Return:             +6.34%
Max Drawdown:           -3.45%

Total Trades:           8
Buy Orders:             4
Sell Orders:            4
Winning Trades:         3
Losing Trades:          1
Win Rate:               75.0%
Average Win:            $23.45
Average Loss:           $12.30

Final Position:
  Cash:                 $1,045.23
  Shares Held:          0
  Stock Value:          $0.00

📈 BENCHMARK (Buy & Hold):
--------------------------------------------------------------------------------
Strategy:               Buy 5 shares at $189.45 and hold
Final Value:            $1,021.35
Return:                 +2.13%

Strategy vs Benchmark:  +2.39% ✅ OUTPERFORM
```

---

## 🔍 How Signals Are Generated

Each day, the system analyzes:

### Technical Indicators
1. **RSI (Relative Strength Index)**
   - < 30: Oversold (buy signal)
   - \> 70: Overbought (sell signal)

2. **MACD (Moving Average Convergence Divergence)**
   - Bullish crossover: Buy signal
   - Bearish crossover: Sell signal

3. **Moving Averages (20, 50, 200-day)**
   - Golden Cross (20 > 50 > 200): Strong uptrend
   - Death Cross (20 < 50 < 200): Strong downtrend

4. **Bollinger Bands**
   - Price < Lower Band: Oversold
   - Price > Upper Band: Overbought

5. **Volume Analysis**
   - High volume: Confirms trend
   - Low volume: Weak trend

### Fundamental Factors
- P/E Ratio, ROE, Profit Margins, Debt/Equity
- (Uses static data from `fundamental_data.json`)

### Sentiment Factors
- News sentiment, market mood
- (Uses static data from `sentiment_data.json`)

---

## ⚙️ Customization

You can adjust these parameters in the scripts:

### `backtest_signals.py`
```python
START_DATE = "2024-09-03"  # Change backtest start
END_DATE = "2024-10-03"    # Change backtest end
SYMBOL = "IBM"             # Change stock symbol
```

### `analyze_backtest_performance.py`
```python
INITIAL_CAPITAL = 1000.0   # Change starting capital
COMMISSION_RATE = 0.0      # Add trading fees (0.001 = 0.1%)
```

### Trading Strategy Rules
Modify the `execute_strategy()` function to change how signals trigger trades.

---

## 🎓 Understanding Results

### Good Performance Indicators:
- ✅ Positive total return
- ✅ Win rate > 60%
- ✅ Outperformance vs buy-and-hold
- ✅ Max drawdown < 10%

### Warning Signs:
- ⚠️ Negative total return
- ⚠️ Win rate < 40%
- ⚠️ Underperformance vs buy-and-hold
- ⚠️ Max drawdown > 20%

### Key Metrics Explained:

**Total Return**: Overall profit/loss  
**Win Rate**: % of profitable trades  
**Max Drawdown**: Largest peak-to-trough decline  
**Outperformance**: Return above buy-and-hold strategy  

---

## 🚨 Important Notes

1. **No Look-Ahead Bias**: Signals use only data available up to that date
2. **Transaction Costs**: Currently set to $0 (can add commission)
3. **Slippage**: Not modeled (assumes you get exact prices)
4. **Market Orders**: Assumes all orders execute at close price
5. **Partial Shares**: Not allowed (buys whole shares only)
6. **Dividends**: Not included in returns
7. **Website Not Affected**: This is completely separate analysis

---

## 📞 Next Steps

After running the backtest:

1. **Review Signal Quality**: Check `backtest_results.json` for daily explanations
2. **Analyze Trades**: Review `backtest_transactions.json` for entry/exit points
3. **Check Performance**: Look at metrics to see if strategy is profitable
4. **Compare to Benchmark**: Did you beat buy-and-hold?
5. **Identify Patterns**: Which signals worked best? Which failed?
6. **Optimize Strategy**: Adjust signal thresholds or trading rules
7. **Test Different Periods**: Try different date ranges
8. **Test Other Stocks**: Change SYMBOL to test on different companies

---

## 🔧 Troubleshooting

### "Price data not found"
- Ensure `IBM/price_data.csv` exists
- Check date format in CSV is correct

### "No data for backtest period"
- Adjust START_DATE and END_DATE to match available data
- Check that date range includes trading days

### "Insufficient historical data"
- Need at least 200 days of history for technical indicators
- Extend data collection period

---

## 📊 Sample Analysis Workflow

```bash
# 1. Run backtest
run_backtest.bat

# 2. Review signals
# Open: backtest_results.json
# Look for: High confidence signals, detailed reasons

# 3. Check transactions
# Open: backtest_transactions.json
# Verify: Buy/sell decisions make sense

# 4. Analyze performance
# Open: backtest_metrics.json
# Compare: Your strategy vs buy-and-hold

# 5. Optimize
# Adjust thresholds in backtest_signals.py
# Re-run and compare results
```

---

**Last Updated**: October 10, 2024  
**Version**: 1.0  
**Status**: Ready for Testing ✅
