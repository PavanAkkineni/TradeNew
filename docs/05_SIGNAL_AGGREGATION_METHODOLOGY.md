# Signal Aggregation Methodology - Combining Insights for Final Trade Signals

## Overview
This guide explains how to combine technical, fundamental, sentiment, and alternative data signals into a unified, actionable trade signal with confidence scoring.

---

## The Challenge

You now have **multiple independent signals**:
- **Technical Signal**: Buy (RSI oversold, MACD bullish crossover)
- **Fundamental Signal**: Hold (Fair valuation, moderate growth)
- **Sentiment Signal**: Sell (Negative news trend)
- **Alternative Signal**: Buy (Insider buying)

**Question**: What's the final action?

This guide provides the framework to systematically aggregate conflicting signals.

---

## Signal Aggregation Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    STEP 1: SIGNAL NORMALIZATION                 │
│  Convert all signals to common scale: -100 to +100              │
│  -100 = Strong Sell | 0 = Neutral | +100 = Strong Buy          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                 STEP 2: CONFIDENCE SCORING                      │
│  Each signal has confidence: 0.0 (uncertain) to 1.0 (certain)   │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                   STEP 3: CATEGORY WEIGHTING                    │
│  Technical: 40% | Fundamental: 30% | Sentiment: 20% | Alt: 10%  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  STEP 4: TIME DECAY ADJUSTMENT                  │
│  Recent data weighted higher than older data                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  STEP 5: CONFLICT RESOLUTION                    │
│  Handle contradictory signals based on strength and confidence  │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                 STEP 6: AGGREGATION CALCULATION                 │
│  Weighted average with confidence scaling                       │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                STEP 7: POSITION SIZE DETERMINATION              │
│  Higher confidence + stronger signal = Larger position          │
└────────────────────────┬────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                    FINAL TRADE SIGNAL                           │
│  Action | Confidence | Position Size | Risk Level               │
└─────────────────────────────────────────────────────────────────┘
```

---

## STEP 1: Signal Normalization

### Converting All Signals to -100 to +100 Scale

#### Technical Signals

**From Technical Indicators**:

**RSI (0-100)**:
```
if RSI < 30: signal = map(RSI, 0, 30, -100, -50)  # Oversold = Bullish
elif RSI < 50: signal = map(RSI, 30, 50, -50, 0)
elif RSI < 70: signal = map(RSI, 50, 70, 0, +50)
else: signal = map(RSI, 70, 100, +50, +100)  # Overbought = Peak risk
```

**MACD**:
```
if MACD_line > Signal_line and MACD > 0: signal = +60 to +80
elif MACD_line > Signal_line and MACD < 0: signal = +30 to +50
elif MACD_line < Signal_line and MACD > 0: signal = -30 to -50
else: signal = -60 to -80
```

**Moving Average Position**:
```
Price > 200_SMA > 50_SMA > 20_SMA: signal = +80 (strong uptrend)
Price > 50_SMA > 20_SMA: signal = +50 (uptrend)
Price between 20_SMA and 50_SMA: signal = 0 (neutral)
Price < 50_SMA < 200_SMA: signal = -50 (downtrend)
Price < 200_SMA < 50_SMA < 20_SMA: signal = -80 (strong downtrend)
```

**Volume**:
```
Volume > 2x avg: Amplify base signal by 1.2x
Volume > 1.5x avg: Amplify by 1.1x
Volume < 0.5x avg: Dampen by 0.8x
```

**Combined Technical Score**:
```
Technical_Signal = (
    RSI_signal × 0.25 +
    MACD_signal × 0.25 +
    MA_signal × 0.30 +
    Momentum_signal × 0.20
) × Volume_multiplier
```

---

#### Fundamental Signals

**Growth Score** (Revenue & EPS Growth):
```
if EPS_growth > 25%: signal = +80 to +100
elif EPS_growth > 15%: signal = +50 to +80
elif EPS_growth > 5%: signal = +20 to +50
elif EPS_growth > 0%: signal = 0 to +20
elif EPS_growth > -10%: signal = -20 to 0
else: signal = -50 to -100
```

**Valuation Score** (P/E vs sector, PEG):
```
if PEG < 1 and P/E < sector_avg: signal = +70 (undervalued)
elif PEG < 1.5 and P/E < sector_avg: signal = +40
elif PEG < 2: signal = 0 (fairly valued)
elif PEG < 3: signal = -40
else: signal = -70 (overvalued)
```

**Quality Score** (Margins, ROE, Cash Flow):
```
if ROE > 20% and FCF_margin > 15%: signal = +80
elif ROE > 15% and FCF_margin > 10%: signal = +50
elif ROE > 10% and FCF_margin > 5%: signal = +20
elif ROE > 5%: signal = 0
else: signal = -50
```

**Financial Health Score** (Debt, Liquidity):
```
if Current_ratio > 2 and Debt_to_Equity < 0.5: signal = +70
elif Current_ratio > 1.5 and Debt_to_Equity < 1: signal = +40
elif Current_ratio > 1 and Debt_to_Equity < 2: signal = 0
else: signal = -60
```

**Combined Fundamental Score**:
```
Fundamental_Signal = (
    Growth_score × 0.35 +
    Valuation_score × 0.30 +
    Quality_score × 0.20 +
    Health_score × 0.15
)
```

---

#### Sentiment Signals

**News Sentiment** (90-day weighted):
```
Weighted_sentiment = Σ(sentiment_i × relevance_i × e^(-0.05×days_ago_i))

if Weighted_sentiment > 0.6: signal = +80
elif Weighted_sentiment > 0.3: signal = +50
elif Weighted_sentiment > -0.3: signal = 0
elif Weighted_sentiment > -0.6: signal = -50
else: signal = -80
```

**Earnings Call Sentiment**:
```
Confident + Optimistic tone + Guidance raise: signal = +70
Confident + Stable tone: signal = +30
Neutral tone: signal = 0
Defensive + Cautious: signal = -40
Defensive + Guidance cut: signal = -80
```

**Analyst Estimate Revisions**:
```
if Upgrades > Downgrades by 3+: signal = +60
elif Upgrades > Downgrades: signal = +30
elif Upgrades == Downgrades: signal = 0
elif Downgrades > Upgrades: signal = -30
else: signal = -60
```

**Combined Sentiment Score**:
```
Sentiment_Signal = (
    News_sentiment × 0.40 +
    Earnings_call_sentiment × 0.35 +
    Estimate_revisions × 0.25
)
```

---

#### Alternative Data Signals

**Insider Transactions**:
```
Net_insider_value = Total_buys - Total_sells (last 12 months)

if Net > $5M and Multiple_execs: signal = +90
elif Net > $1M: signal = +60
elif Net > $100k: signal = +30
elif Net > -$500k: signal = 0
elif Net > -$5M: signal = -40
else: signal = -70
```

**Options Flow** (if using):
```
Call_volume / Put_volume ratio (normalized)

if C/P > 2.0: signal = +70
elif C/P > 1.5: signal = +40
elif C/P > 0.8: signal = 0
elif C/P > 0.5: signal = -40
else: signal = -70
```

**Combined Alternative Score**:
```
Alternative_Signal = (
    Insider_signal × 0.70 +
    Options_signal × 0.30
)
```

---

## STEP 2: Confidence Scoring

Each signal gets a confidence score (0.0 to 1.0).

### Factors Affecting Confidence

#### Data Quality Confidence
```
if Data_completeness > 95%: quality_conf = 1.0
elif Data_completeness > 80%: quality_conf = 0.8
elif Data_completeness > 60%: quality_conf = 0.6
else: quality_conf = 0.3
```

#### Signal Strength Confidence
```
Signal_strength_conf = |Signal_value| / 100

Example:
Signal = +80 → confidence boost = 0.8
Signal = +20 → confidence boost = 0.2
```

#### Historical Accuracy Confidence
```
if Signal has been backtested:
    accuracy_conf = Win_rate / 100
    
Example:
This signal pattern worked 75% of time historically → accuracy_conf = 0.75
```

#### Indicator Agreement Confidence
```
Within category agreement:

Technical category:
    if RSI, MACD, MA all agree (same direction): agreement_conf = 1.0
    if 2 of 3 agree: agreement_conf = 0.7
    if all disagree: agreement_conf = 0.3
```

#### Time Relevance Confidence
```
Data_age_conf = e^(-0.05 × days_old)

Fresh data (< 7 days): conf = 0.9-1.0
Week old: conf = 0.7
Month old: conf = 0.6
```

### Combined Confidence Formula

```python
def calculate_confidence(signal):
    confidence = (
        data_quality_conf × 0.20 +
        signal_strength_conf × 0.25 +
        historical_accuracy_conf × 0.25 +
        indicator_agreement_conf × 0.20 +
        time_relevance_conf × 0.10
    )
    
    return min(confidence, 1.0)  # Cap at 1.0
```

---

## STEP 3: Category Weighting

Different trading styles → different weights.

### Default Weighting (Balanced Approach)

```
Technical: 40%
Fundamental: 30%
Sentiment: 20%
Alternative: 10%
```

**Rationale**:
- Technical drives entry/exit timing
- Fundamentals provide margin of safety
- Sentiment identifies catalysts
- Alternative data confirms or warns

### Alternative Weighting Schemes

#### Day Trading (Short-term, < 1 day hold)
```
Technical: 60%
Sentiment: 25%
Alternative: 15%
Fundamental: 0%
```
*Fundamentals don't matter for intraday*

#### Swing Trading (Days to weeks)
```
Technical: 50%
Fundamental: 20%
Sentiment: 20%
Alternative: 10%
```
*Technical dominates, fundamentals provide context*

#### Position Trading (Weeks to months)
```
Technical: 30%
Fundamental: 40%
Sentiment: 20%
Alternative: 10%
```
*Fundamentals drive, technical for timing*

#### Long-term Investing (Months to years)
```
Technical: 15%
Fundamental: 60%
Sentiment: 15%
Alternative: 10%
```
*Fundamentals dominate, technical barely matters*

#### Growth Investing
```
Technical: 25%
Fundamental: 45% (growth metrics weighted higher)
Sentiment: 20%
Alternative: 10%
```

#### Value Investing
```
Technical: 20%
Fundamental: 50% (valuation weighted higher)
Sentiment: 15%
Alternative: 15% (insiders important for value)
```

---

## STEP 4: Time Decay Adjustment

Recent data more relevant than old data.

### Decay Function

```python
def time_decay(days_ago, half_life=30):
    """
    half_life: Days for signal to decay to 50% weight
    """
    decay_factor = 0.5 ** (days_ago / half_life)
    return decay_factor
```

### Decay by Signal Type

**Technical Signals**:
- Half-life: 7 days (fast decay)
- Price action changes quickly

**Fundamental Signals**:
- Half-life: 90 days (slow decay)
- Fundamentals change slowly

**Sentiment Signals**:
- Half-life: 14 days (medium decay)
- News relevance fades

**Alternative Signals**:
- Half-life: 30 days (medium decay)
- Insider activity has lasting effect

### Application

```python
adjusted_signal = base_signal × time_decay(data_age, half_life)
```

---

## STEP 5: Conflict Resolution

What to do when signals disagree?

### Conflict Types

#### Strong Disagreement
**Example**: Technical = +80, Fundamental = -70

**Resolution Strategy**:
1. Check confidence scores
   - If Technical confidence = 0.9, Fundamental confidence = 0.4 → Trust technical
   - If both high confidence → Reduce position size, wait for alignment

2. Check timeframe mismatch
   - Technical (short-term) vs Fundamental (long-term) can both be right
   - Different timescales, different signals

3. Check for special situations
   - Fundamental bearish but technical bullish = Potential short squeeze
   - Fundamental bullish but technical bearish = Accumulation opportunity

#### Moderate Disagreement
**Example**: Technical = +60, Fundamental = -20

**Resolution**:
- Net positive still
- Proceed with caution
- Smaller position size
- Tighter risk management

#### Sentiment vs Fundamentals
**Example**: Fundamentals strong (+70) but Sentiment weak (-60)

**Interpretation**:
- Contrarian opportunity (market pessimistic on good company)
- OR market knows something fundamentals don't show yet
- **Resolution**: Wait for sentiment to improve OR fundamentals to weaken (alignment)

### Conflict Resolution Rules

**Rule 1: Confidence Wins**
```
if abs(Signal_A) > abs(Signal_B) and Confidence_A > Confidence_B:
    Weight_A higher
```

**Rule 2: Majority Alignment**
```
if 3 out of 4 categories agree:
    Trust the majority
    Outlier category likely noise or early signal
```

**Rule 3: Veto Power**
```
if Any category shows EXTREME signal (>|90|) with high confidence:
    Reduce overall position regardless of other signals
    
Example: Fundamental = -95 (bankruptcy risk)
→ Don't buy even if technical is bullish
```

**Rule 4: Wait for Alignment**
```
if Disagreement_score > 50 (large conflicts):
    Final_signal = HOLD / WAIT
    Required_alignment_threshold before entry
```

---

## STEP 6: Aggregation Calculation

### Formula

```python
def aggregate_signals(signals, confidences, weights):
    """
    signals: dict of category signals (-100 to +100)
    confidences: dict of category confidences (0 to 1)
    weights: dict of category weights (sum to 1.0)
    """
    
    # Confidence-weighted signal
    weighted_sum = 0
    confidence_sum = 0
    
    for category in signals:
        signal = signals[category]
        confidence = confidences[category]
        weight = weights[category]
        
        weighted_sum += signal × confidence × weight
        confidence_sum += confidence × weight
    
    # Normalize by total confidence
    if confidence_sum > 0:
        final_signal = weighted_sum / confidence_sum
    else:
        final_signal = 0
    
    # Overall confidence
    final_confidence = confidence_sum
    
    return final_signal, final_confidence
```

### Example Calculation

**Inputs**:
```
Signals:
- Technical: +70
- Fundamental: +40
- Sentiment: +20
- Alternative: +60

Confidences:
- Technical: 0.85
- Fundamental: 0.90
- Sentiment: 0.60
- Alternative: 0.70

Weights (Swing Trading):
- Technical: 0.50
- Fundamental: 0.20
- Sentiment: 0.20
- Alternative: 0.10
```

**Calculation**:
```
Technical contribution: 70 × 0.85 × 0.50 = 29.75
Fundamental contribution: 40 × 0.90 × 0.20 = 7.20
Sentiment contribution: 20 × 0.60 × 0.20 = 2.40
Alternative contribution: 60 × 0.70 × 0.10 = 4.20

Weighted sum: 29.75 + 7.20 + 2.40 + 4.20 = 43.55

Confidence sum: (0.85×0.50) + (0.90×0.20) + (0.60×0.20) + (0.70×0.10)
                = 0.425 + 0.18 + 0.12 + 0.07 = 0.795

Final signal: 43.55 / 0.795 = 54.78
Final confidence: 0.795
```

**Interpretation**:
- Signal: +54.78 → **BUY**
- Confidence: 0.795 → **HIGH** (79.5%)

---

## STEP 7: Position Size Determination

Position size = f(Signal_strength, Confidence, Risk_tolerance)

### Kelly Criterion (Modified)

```python
def calculate_position_size(
    signal_strength,     # -100 to +100
    confidence,          # 0 to 1
    win_rate,           # Historical win rate (0 to 1)
    avg_win_loss_ratio, # Average win / average loss
    max_risk_percent    # Max % of portfolio to risk (e.g., 0.02 = 2%)
):
    # Kelly formula: f = (p × b - q) / b
    # p = win probability
    # q = loss probability = 1 - p
    # b = win/loss ratio
    
    p = win_rate
    q = 1 - win_rate
    b = avg_win_loss_ratio
    
    kelly_fraction = (p × b - q) / b
    
    # Adjust by signal strength and confidence
    adjusted_kelly = kelly_fraction × (abs(signal_strength) / 100) × confidence
    
    # Use fractional Kelly (safer)
    fractional_kelly = adjusted_kelly × 0.25  # Quarter Kelly
    
    # Cap at max risk
    position_size = min(fractional_kelly, max_risk_percent)
    
    # Don't go below minimum
    position_size = max(position_size, 0.01) if signal_strength > 0 else 0
    
    return position_size
```

### Simplified Position Sizing

**If you don't have backtested win rates**:

```python
def simple_position_size(signal_strength, confidence, base_position=0.05):
    """
    base_position: Standard position size (e.g., 5% of portfolio)
    """
    
    # Scale by signal strength
    strength_multiplier = abs(signal_strength) / 100
    
    # Scale by confidence
    confidence_multiplier = confidence
    
    # Calculate position
    position = base_position × strength_multiplier × confidence_multiplier
    
    # Apply limits
    position = max(0.01, min(position, 0.10))  # 1% to 10% max
    
    return position
```

### Position Size Categories

| Signal | Confidence | Position Size | Example (on $100k portfolio) |
|--------|-----------|---------------|------------------------------|
| 80-100 | 0.9-1.0   | 8-10%        | $8,000 - $10,000            |
| 60-80  | 0.8-0.9   | 5-8%         | $5,000 - $8,000             |
| 40-60  | 0.7-0.8   | 3-5%         | $3,000 - $5,000             |
| 20-40  | 0.6-0.7   | 1-3%         | $1,000 - $3,000             |
| 0-20   | <0.6      | 0-1%         | WAIT or SKIP                |

**Direction**:
- Positive signal → Long position
- Negative signal → Short position (or exit long)

---

## STEP 8: Final Signal Output

### Output Structure

```json
{
  "symbol": "IBM",
  "timestamp": "2025-10-01T23:00:00Z",
  "final_signal": {
    "value": 54.78,
    "action": "BUY",
    "strength": "MODERATE",
    "confidence": 0.795
  },
  "component_signals": {
    "technical": {"value": 70, "confidence": 0.85, "weight": 0.50},
    "fundamental": {"value": 40, "confidence": 0.90, "weight": 0.20},
    "sentiment": {"value": 20, "confidence": 0.60, "weight": 0.20},
    "alternative": {"value": 60, "confidence": 0.70, "weight": 0.10}
  },
  "position_recommendation": {
    "position_size_percent": 5.2,
    "entry_price_target": 286.00,
    "stop_loss": 275.00,
    "take_profit_1": 295.00,
    "take_profit_2": 305.00
  },
  "risk_metrics": {
    "risk_level": "MEDIUM",
    "max_drawdown_expected": "5-8%",
    "hold_period": "2-4 weeks"
  },
  "reasoning": [
    "Strong technical setup with bullish MACD crossover",
    "Solid fundamentals with improving margins",
    "Recent insider buying supports thesis",
    "Sentiment neutral to slightly positive"
  ]
}
```

### Action Categories

| Signal Range | Action | Description |
|--------------|--------|-------------|
| +70 to +100 | **STRONG BUY** | High conviction, large position |
| +40 to +70 | **BUY** | Moderate conviction, standard position |
| +20 to +40 | **WEAK BUY** | Low conviction, small position |
| -20 to +20 | **HOLD** | Wait for clearer signal |
| -40 to -20 | **WEAK SELL** | Consider exit, reduce position |
| -70 to -40 | **SELL** | Exit position |
| -100 to -70 | **STRONG SELL** | Exit immediately, consider short |

---

## Implementation Workflow

### Daily Process

**1. Data Collection (Morning)**:
- Fetch overnight news
- Update price data
- Check for insider transactions
- Review earnings calendar

**2. Signal Calculation (Pre-market)**:
- Calculate technical indicators
- Update fundamental scores (if new data)
- Aggregate sentiment
- Compute individual category signals

**3. Aggregation (Before open)**:
- Run aggregation algorithm
- Generate final signals
- Calculate position sizes
- Set entry/exit targets

**4. Execution (Market hours)**:
- Place orders based on signals
- Monitor fills
- Adjust stops/targets

**5. Review (After hours)**:
- Analyze what worked/didn't work
- Update model parameters
- Log for backtesting

### Weekly Process

- Review fundamental data updates
- Check earnings transcripts
- Analyze weekly charts
- Rebalance portfolio

### Monthly Process

- Full fundamental review
- Backtest signal accuracy
- Adjust weights if needed
- Performance attribution

---

## FinLLM Integration Points

### Signal Generation
```
Prompt: "Analyze the following data for IBM and generate a trade signal:
- Technical indicators: [data]
- Fundamental metrics: [data]
- Recent news: [data]
- Insider transactions: [data]

Provide:
1. Overall signal (Buy/Sell/Hold)
2. Confidence level (0-100)
3. Key supporting factors
4. Key risks
5. Recommended position size
6. Price targets"
```

### Conflict Resolution
```
Prompt: "I have conflicting signals for IBM:
- Technical: Strong Buy (+80, conf 0.85)
- Fundamental: Weak Sell (-30, conf 0.90)

Explain:
1. Why might these conflict?
2. Which should I trust more?
3. What additional data would resolve this?
4. What's your final recommendation?"
```

### Risk Assessment
```
Prompt: "Given this aggregated signal:
Signal: +55, Confidence: 0.75

And these positions:
- IBM: 5% of portfolio
- AAPL: 8% of portfolio
- MSFT: 6% of portfolio

Assess:
1. Is this position size appropriate?
2. Portfolio concentration risk?
3. Correlation risk?
4. Recommended adjustments?"
```

---

## Backtesting the Aggregation

### Track These Metrics

**Signal Accuracy**:
- Win rate (% profitable trades)
- Avg win vs avg loss
- Sharpe ratio
- Max drawdown

**By Signal Strength**:
- How well do "Strong Buy" signals perform vs "Weak Buy"?
- Optimal thresholds for action

**By Confidence**:
- Do high-confidence signals outperform?
- Confidence calibration (are 80% confidence trades right 80% of time?)

**By Category**:
- Which category has highest predictive power?
- Should weights be adjusted?

### Continuous Improvement

```python
# Example adjustment based on backtest
if technical_signals_win_rate > 0.70 and fundamental_win_rate < 0.55:
    # Increase technical weight
    weights['technical'] += 0.05
    weights['fundamental'] -= 0.05
```

---

## Key Takeaways

### Core Principles

1. **Normalization is critical**: All signals must be on same scale
2. **Confidence matters**: Signal × Confidence, not just signal
3. **Recency matters**: Fresh data weighted higher
4. **No single signal is enough**: Aggregation reduces noise
5. **Backtesting is essential**: Validate before live trading

### Best Practices

- Start with equal weights, adjust based on performance
- Require minimum confidence threshold (e.g., 0.6) before action
- Don't override the system emotionally
- Log all signals for analysis
- Review and iterate monthly

### Warning Signs

- **All signals maxed out** (±100): Probably overfitting
- **Confidence always high**: Not calibrated properly
- **No holds/waits**: Too aggressive
- **Too many conflicts**: Need better data or different stocks

---

## Complete Example: IBM Analysis

### Raw Data Collection
- Daily Adjusted: 2 years ✓
- Income Statement: 5 years ✓
- News Sentiment: 90 days ✓
- Insider Transactions: 12 months ✓

### Individual Signals
**Technical** (+70, conf 0.85):
- RSI: 45 (neutral)
- MACD: Bullish crossover
- Price > 50 SMA > 200 SMA
- Volume above average

**Fundamental** (+40, conf 0.90):
- Revenue growth: 8% YoY (moderate)
- EPS growth: 12% YoY (good)
- P/E: 18 vs sector 22 (cheap)
- FCF positive and growing
- ROE: 16% (good)

**Sentiment** (+20, conf 0.60):
- News sentiment: +0.25 (mildly positive)
- Last earnings call: confident tone
- No major negative news
- Estimate revisions: neutral

**Alternative** (+60, conf 0.70):
- 3 insider buys last month ($2M total)
- No insider selling
- Call/put ratio: 1.4 (bullish bias)

### Aggregation
Weights (swing trading): T:50%, F:20%, S:20%, A:10%

```
Final_signal = (70×0.85×0.50 + 40×0.90×0.20 + 20×0.60×0.20 + 60×0.70×0.10) 
               / (0.85×0.50 + 0.90×0.20 + 0.60×0.20 + 0.70×0.10)
             = 54.78 / 0.795
             = ~55
```

### Final Output
- **Action**: BUY
- **Confidence**: 79.5%
- **Position Size**: 5% of portfolio
- **Entry**: $286
- **Stop Loss**: $275 (-4%)
- **Target 1**: $295 (+3%)
- **Target 2**: $305 (+6.6%)
- **Hold Period**: 2-4 weeks

---

**COMPLETE - Ready for Implementation**
