# Price Data Guide - Technical Analysis Foundation

## Overview
Price data forms the backbone of technical analysis. This guide covers all time-based price APIs and their optimal usage for trading signal generation.

---

## 1. Intraday Data (TIME_SERIES_INTRADAY)

### Description
High-frequency OHLCV (Open, High, Low, Close, Volume) data with intervals from 1 minute to 60 minutes.

### Intervals Available
- **1min**: Ultra-short scalping (not recommended for beginners)
- **5min**: Day trading and intraday patterns ✅ **RECOMMENDED**
- **15min**: Intraday swing trades
- **30min**: Session-based analysis
- **60min**: Intraday trend confirmation

### Historical Data Required
**Minimum**: 30 days  
**Recommended**: 30-60 days  
**Maximum useful**: 90 days

### Why This Timeframe?
- **30 days** = ~22 trading days = Enough for short-term pattern recognition
- Captures recent market regime and volatility characteristics
- Sufficient for calculating intraday moving averages (20-period on 5min)
- Balances data volume with relevance (older intraday data loses predictive value)
- API efficiency: Full month data without excessive API calls

### Use Cases
1. **Day Trading Signals**: Entry/exit within single session
2. **Pattern Recognition**: Head & shoulders, triangles, flags on intraday charts
3. **Volume Profile**: Intraday support/resistance levels
4. **Momentum Trading**: Quick moves based on breaking levels
5. **Scalping**: Very short-term price movements (1-5min intervals)

### Technical Indicators to Calculate
- **Trend**: 9-EMA, 21-EMA crossovers
- **Momentum**: RSI(14), Stochastic(14,3,3)
- **Volume**: VWAP, Volume spikes vs 20-period average
- **Volatility**: Bollinger Bands(20,2)
- **Support/Resistance**: Previous day high/low, pivot points

### Storage Considerations
- 5min interval, 30 days = ~2,500 data points per symbol
- File size: ~300-500 KB JSON per symbol
- Update frequency: End of day (EOD) for historical, realtime if premium

---

## 2. Daily Data (TIME_SERIES_DAILY)

### Description
Daily OHLCV data, not adjusted for splits/dividends. Use for raw price analysis.

### Historical Data Required
**Minimum**: 100 days  
**Recommended**: 252 days (1 year)  
**Optimal**: 504 days (2 years)  
**Maximum useful**: 1,260 days (5 years)

### Why 252 Days (1 Year)?
- **252** = Average trading days per year
- **200-day SMA**: Most widely followed long-term moving average
- **1 year** captures full seasonal cycle
- **Earnings cycles**: 4 complete quarterly reports
- **Technical patterns**: Sufficient for reliable trend identification

### Use Cases
1. **Swing Trading**: 2-10 day holding periods
2. **Position Trading Setup**: Weekly to monthly holds
3. **Backtesting**: Strategy validation
4. **Seasonal Analysis**: Yearly patterns
5. **Raw Price Comparison**: Without adjustment distortions

### Key Indicators (1-Year Data)
- **SMA**: 20, 50, 100, 200-day
- **EMA**: 12, 26, 50-day
- **MACD**: 12, 26, 9 settings
- **RSI**: 14-day
- **Bollinger Bands**: 20-day, 2 std dev
- **ADX**: 14-day (trend strength)

### Why 2 Years (504 Days)?
- **Comparative analysis**: YoY comparisons
- **Longer trend validation**: Multi-year trends
- **Bear/bull cycle capture**: Different market conditions
- **Reliability**: More data = better statistical significance

---

## 3. Daily Adjusted (TIME_SERIES_DAILY_ADJUSTED) ⭐ **PRIMARY DATA SOURCE**

### Description
Daily OHLCV adjusted for splits and dividends. **CRITICAL** for accurate analysis.

### Historical Data Required
**Minimum**: 252 days (1 year)  
**Recommended**: 504 days (2 years) ✅  
**Optimal**: 756 days (3 years)  
**Maximum useful**: 2,520 days (10 years)

### Why Adjusted Data is Critical?
- **Stock Splits**: Without adjustment, 2-for-1 split appears as 50% price drop
- **Dividends**: Adjust for dividend payments to show true total return
- **Accurate Backtesting**: Historical strategies need clean data
- **Indicator Calculation**: Moving averages meaningless without adjustment
- **Comparative Analysis**: Fair comparison across time periods

### Why 2 Years Recommended?
1. **Complete business cycles**: Captures different market conditions
2. **Reliable statistics**: Better mean reversion calculations
3. **Pattern validation**: Confirm recurring patterns
4. **YoY growth metrics**: Calculate year-over-year comparisons
5. **Seasonal patterns**: Identify multi-year seasonal trends
6. **Volatility regimes**: Different volatility environments

### Use Cases
1. **Primary Technical Analysis**: This is your main dataset
2. **Backtesting Trading Strategies**: Accurate historical simulation
3. **Risk Metrics**: Calculate beta, Sharpe ratio, max drawdown
4. **Correlation Analysis**: Compare with indices, sectors
5. **Machine Learning Training**: Feature engineering for models

### Essential Calculations
**With 2 Years Data**:
- All moving averages up to 200-day
- Annualized volatility (252-day std dev)
- 52-week high/low tracking
- Beta vs S&P 500 (rolling 252-day)
- Maximum drawdown analysis
- Risk-adjusted returns (Sharpe, Sortino)

### Advanced Indicators (2+ Years)
- **Ichimoku Cloud**: Needs 52+ periods
- **Keltner Channels**: 20-day with ATR
- **Donchian Channels**: 20-day breakouts
- **Parabolic SAR**: Trend following
- **Williams %R**: Momentum oscillator

---

## 4. Weekly Data (TIME_SERIES_WEEKLY)

### Description
Weekly OHLCV data, unadjusted. Each data point represents one week.

### Historical Data Required
**Minimum**: 52 weeks (1 year)  
**Recommended**: 104 weeks (2 years)  
**Optimal**: 156 weeks (3 years)  
**Maximum useful**: 520 weeks (10 years)

### Why This Timeframe?
- **52 weeks** = 1 year, minimum for trend analysis
- **104 weeks** = 2 years, better trend reliability
- **156 weeks** = 3 years, captures market cycles ✅ **SWEET SPOT**

### Use Cases
1. **Medium-term Trend Identification**: Multi-week to multi-month trends
2. **Noise Reduction**: Filters out daily volatility
3. **Position Trading**: Longer holding periods (weeks to months)
4. **Divergence Analysis**: Weekly vs daily signal conflicts
5. **Market Cycle Analysis**: Identify larger wave patterns

### Weekly vs Daily - When to Use?
- **Weekly signals**: More reliable, fewer false signals
- **Daily signals**: More granular, faster response
- **Best practice**: Weekly for direction, daily for entry/exit timing

### Key Weekly Indicators
- **EMA**: 13, 26, 52-week
- **MACD Weekly**: 12,26,9 (slower than daily)
- **RSI Weekly**: 14-week (major overbought/oversold)
- **Support/Resistance**: Multi-month levels

---

## 5. Weekly Adjusted (TIME_SERIES_WEEKLY_ADJUSTED)

### Description
Weekly OHLCV adjusted for splits and dividends.

### Historical Data Required
**Minimum**: 104 weeks (2 years)  
**Recommended**: 156 weeks (3 years) ✅  
**Optimal**: 260 weeks (5 years)

### Why 3 Years (156 Weeks)?
1. **Market cycles**: Typical bull/bear cycles are 3-5 years
2. **Statistical significance**: Enough data for reliable patterns
3. **Regime changes**: Captures different macro environments
4. **Backtesting**: Validates strategies across conditions
5. **Long-term trends**: Identifies sustainable directional moves

### Use Cases
1. **Primary Weekly Analysis**: Use this over unadjusted weekly
2. **Swing Trading**: Multi-week holding periods
3. **Trend Following**: Major trend identification
4. **Portfolio Management**: Long-term allocation decisions
5. **Risk Management**: Weekly volatility patterns

### Strategic Indicators
- **Trend Strength**: ADX on weekly (very reliable)
- **Momentum**: Weekly RSI crossing 50 (bullish/bearish)
- **Moving Averages**: 13/26 EMA crossovers (major signals)
- **Breakouts**: Weekly high/low breaks are significant

---

## 6. Monthly Data (TIME_SERIES_MONTHLY)

### Description
Monthly OHLCV data, unadjusted. One data point per month.

### Historical Data Required
**Minimum**: 24 months (2 years)  
**Recommended**: 36 months (3 years)  
**Optimal**: 60 months (5 years) ✅  
**Maximum useful**: 120-240 months (10-20 years)

### Why 5 Years (60 Months)?
- **Economic cycles**: Full business cycle ~5-7 years
- **Long-term trends**: Distinguish noise from real trends
- **Structural changes**: Company transformations visible
- **Macro analysis**: Correlation with economic indicators
- **Historical context**: Compare current vs historical norms

### Use Cases
1. **Long-term Investing**: Buy and hold strategies
2. **Macro Trend Analysis**: Economic cycle positioning
3. **Strategic Allocation**: Long-term portfolio decisions
4. **Historical Context**: Where are we in the cycle?
5. **Retirement Planning**: Decades-long perspectives

### Monthly Indicators
- **SMA**: 12-month (yearly trend), 36-month (3-year trend)
- **Momentum**: 12-month rate of change
- **Volatility**: Annual volatility changes
- **Cyclical Patterns**: Multi-year cycles

---

## 7. Monthly Adjusted (TIME_SERIES_MONTHLY_ADJUSTED)

### Description
Monthly OHLCV adjusted for splits and dividends.

### Historical Data Required
**Minimum**: 36 months (3 years)  
**Recommended**: 60 months (5 years) ✅  
**Optimal**: 120 months (10 years)  
**Maximum useful**: 240+ months (20+ years)

### Why 5-10 Years?
1. **Complete cycles**: Multiple bull/bear markets
2. **Valuation ranges**: Identify historical P/E ranges
3. **Growth trajectory**: Long-term growth rates
4. **Dividend history**: Income investing analysis
5. **Risk metrics**: Long-term volatility and drawdowns

### Use Cases
1. **Long-term Buy/Hold Decisions**: Fundamental long-term value
2. **Pension Fund Analysis**: Multi-decade perspectives
3. **Compound Growth Calculations**: CAGR analysis
4. **Dividend Growth Investing**: Years of dividend increases
5. **Risk Assessment**: Long-term volatility profiles

---

## 8. Quote Endpoint (Realtime/Latest)

### Description
Current price, volume, and key statistics for a symbol.

### Historical Data Required
**Not applicable** - Single snapshot

### Use Cases
1. **Current Market Price**: Real-time or 15-min delayed
2. **Bid/Ask Spreads**: Execution cost estimation
3. **Volume Comparison**: Today vs average
4. **% Change**: Daily performance
5. **Pre-trade Analysis**: Before placing orders

### Data Points
- Latest price, open, high, low
- Volume, previous close
- Change and % change
- 52-week high/low

---

## Data Fetching Strategy

### Priority Order for New Symbol
1. **Daily Adjusted** (2 years) - Start here ✅
2. **Weekly Adjusted** (3 years)
3. **Company Overview** (fundamental context)
4. **Intraday 5min** (30 days) - if day trading
5. **Monthly Adjusted** (5 years) - for context
6. **Quote** (realtime) - before trading

### Storage & Update Schedule
| Data Type | Update Frequency | Storage per Symbol |
|-----------|------------------|-------------------|
| Intraday 5min | Daily (EOD) | ~500 KB |
| Daily Adjusted | Daily (EOD) | ~100 KB (2yr) |
| Weekly Adjusted | Weekly | ~50 KB (3yr) |
| Monthly Adjusted | Monthly | ~20 KB (5yr) |
| Quote | Real-time/15min | ~1 KB |

### API Call Optimization
- **Initial fetch**: Get all historical data once
- **Daily updates**: Only fetch latest day
- **Incremental storage**: Append new data to existing
- **Validation**: Check for splits/dividends → refetch adjusted data if needed

---

## Technical Analysis Workflow

### Multi-Timeframe Analysis

```
Monthly (5yr) → Identify long-term trend direction
        ↓
Weekly (3yr) → Confirm medium-term trend
        ↓
Daily (2yr) → Find swing trade setups
        ↓
Intraday (30d) → Precise entry/exit timing
```

### Signal Strength by Timeframe Alignment

| Monthly | Weekly | Daily | Intraday | Signal Strength |
|---------|--------|-------|----------|----------------|
| ↑ Bull  | ↑ Bull | ↑ Bull| ↑ Bull   | 🟢🟢🟢 STRONG BUY |
| ↑ Bull  | ↑ Bull | ↑ Bull| ↓ Bear   | 🟢🟢 BUY (wait for pullback) |
| ↑ Bull  | ↑ Bull | ↓ Bear| ↓ Bear   | 🟡 HOLD (correction in uptrend) |
| ↑ Bull  | ↓ Bear | ↓ Bear| ↓ Bear   | 🔴 SELL (trend reversal) |
| ↓ Bear  | ↓ Bear | ↓ Bear| ↓ Bear   | 🔴🔴🔴 STRONG SELL |

---

## Key Takeaways

### Critical Data (Must Have)
1. **Daily Adjusted (2 years)** - Primary technical analysis
2. **Weekly Adjusted (3 years)** - Trend confirmation

### High Value Data
3. **Intraday 5min (30 days)** - If day trading
4. **Monthly Adjusted (5 years)** - Long-term context

### Optional
5. **Unadjusted data** - Only if specific use case

### Remember
- **Adjusted data > Unadjusted** for almost all analysis
- **More history ≠ Better** - Diminishing returns after optimal periods
- **Multiple timeframes** - Alignment increases signal reliability
- **Update regularly** - Stale data = Poor decisions

---

**Next**: [Fundamental Data Guide](./03_FUNDAMENTAL_DATA_GUIDE.md)
