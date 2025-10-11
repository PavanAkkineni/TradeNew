# Sentiment & Alternative Data Guide

## Overview
This guide covers sentiment analysis (news, earnings calls) and alternative data sources (insider transactions, market analytics) that provide edge beyond traditional price and fundamental analysis.

---

# PART A: SENTIMENT DATA

## 1. News & Sentiments

### Description
Real-time and historical news articles with AI-powered sentiment scoring for stocks, covering company-specific news, industry trends, and market-moving events.

### Historical Data Required
**Minimum**: 30 days  
**Recommended**: 90 days (3 months) ✅  
**Optimal**: 180 days (6 months)  
**Maximum useful**: 365 days (1 year)

### Why 90 Days (3 Months)?
1. **Recent context**: News relevance degrades quickly
2. **Sentiment trends**: Identify improving/deteriorating narratives
3. **Event clustering**: Multiple related articles = stronger signal
4. **Seasonal patterns**: Quarterly earnings cycles
5. **Model training**: FinLLM needs recent examples for context
6. **Noise filtering**: Distinguish signal from noise over time

### Key Data Points

**Article Metadata**:
- Title, summary, full content
- Source (Bloomberg, Reuters, etc.)
- Publication timestamp
- Relevance score (0-1)

**Sentiment Metrics**:
- **Overall Sentiment**: Bullish/Bearish/Neutral
- **Sentiment Score**: -1.0 (very negative) to +1.0 (very positive)
- **Relevance Score**: How relevant to the stock

**Topic Classification**:
- Earnings
- Product launches
- Legal issues
- Management changes
- Acquisitions/partnerships
- Regulatory
- Market trends

### Sentiment Aggregation Methods

#### Time-Weighted Sentiment Score
More recent news = higher weight

```
Weighted_Score = Σ(Sentiment_i × Relevance_i × Time_Decay_i) / Σ(Weights)
Time_Decay = e^(-λt)  where λ = decay constant, t = days ago
```

**Typical decay**:
- λ = 0.1: News relevant for ~10 days
- λ = 0.05: News relevant for ~20 days

#### Volume-Weighted Sentiment
More articles on same topic = stronger signal

**Calculate**:
1. Count articles per day
2. Average sentiment per day
3. Weight by article volume

**Interpretation**:
- High volume + positive sentiment = Strong bullish signal
- High volume + negative sentiment = Strong bearish signal
- Low volume = Weak signal (ignore)

#### Sentiment Momentum
Rate of change in sentiment

**Calculate**:
- 7-day avg sentiment - 30-day avg sentiment
- Positive = Improving sentiment
- Negative = Deteriorating sentiment

### Use Cases

1. **Catalyst Identification**: News-driven trading opportunities
2. **Risk Management**: Negative news = reduce exposure
3. **Earnings Previews**: Pre-earnings sentiment analysis
4. **Crisis Detection**: Sudden negative sentiment spikes
5. **FinLLM Context**: Feed news to LLM for narrative analysis

### Signal Generation

**STRONG BULLISH** (Score > 0.6):
- High-volume positive news
- Product launch success
- Earnings beat + positive guidance
- Strategic partnerships
- **Action**: Enter long positions, increase allocation

**MODERATE BULLISH** (Score 0.3 to 0.6):
- Positive industry trends
- Minor positive news
- Analyst upgrades
- **Action**: Hold long, consider adding

**NEUTRAL** (Score -0.3 to 0.3):
- Mixed or low-volume news
- No significant catalysts
- **Action**: Maintain positions

**MODERATE BEARISH** (Score -0.6 to -0.3):
- Negative industry trends
- Minor negative news
- Analyst downgrades
- **Action**: Reduce exposure, tighten stops

**STRONG BEARISH** (Score < -0.6):
- High-volume negative news
- Earnings miss + guidance cut
- Legal/regulatory issues
- Management scandals
- **Action**: Exit positions, consider shorts

### FinLLM Analysis Prompts

**For Recent News (7 days)**:
```
Analyze the following news articles about [COMPANY]:
[Articles]

Provide:
1. Key themes and narratives
2. Potential stock impact (bullish/bearish/neutral)
3. Catalysts or risks identified
4. Sentiment trend (improving/stable/deteriorating)
5. Recommended action
```

**For Sentiment Trend (90 days)**:
```
Given 90 days of news sentiment scores for [COMPANY]:
[Time series data]

Identify:
1. Overall sentiment trajectory
2. Significant inflection points
3. Recurring themes
4. Anomalies or outliers
5. Correlation with price movements
```

### Advanced Techniques

**Sentiment Divergence**:
- Compare news sentiment vs price action
- **Positive divergence**: Price down but sentiment improving (contrarian buy)
- **Negative divergence**: Price up but sentiment deteriorating (sell signal)

**Source Credibility Weighting**:
- Weight Bloomberg/Reuters higher than unknown blogs
- Verified sources > Unverified

**Event-Specific Sentiment**:
- Track sentiment before/after specific events
- Measure sentiment shift magnitude

---

## 2. Earnings Call Transcripts

### Description
Full text transcripts of quarterly earnings conference calls, including prepared remarks and Q&A sessions.

### Historical Data Required
**Minimum**: 4 quarters (1 year)  
**Recommended**: 8 quarters (2 years) ✅  
**Optimal**: 12 quarters (3 years)  
**Maximum useful**: 20 quarters (5 years)

### Why 8 Quarters (2 Years)?
1. **Management tone tracking**: Confidence/concern over time
2. **Guidance accuracy**: Track what management says vs delivers
3. **Strategic shifts**: Identify business model changes
4. **YoY comparisons**: Compare same quarter different years
5. **Language pattern changes**: FinLLM can detect subtle shifts
6. **Recession/growth cycles**: Different market conditions

### Key Components

#### Prepared Remarks Section
- **CEO statement**: Strategic overview, performance summary
- **CFO statement**: Financial details, guidance
- **Business unit updates**: Segment performance

#### Q&A Section
- **Analyst questions**: What concerns the street?
- **Management answers**: Tone, confidence, evasiveness
- **Follow-up questions**: Pushback or clarification

### What to Extract

#### Quantitative Guidance
- Revenue guidance (ranges)
- EPS guidance
- Margin expectations
- CapEx plans
- Share buyback intentions

#### Qualitative Themes
- **Growth drivers**: What's working?
- **Challenges**: What's not working?
- **Competitive landscape**: Market positioning
- **Innovation**: New products/services
- **Market conditions**: Macro environment views

### FinLLM Analysis Methods

#### Sentiment Analysis
**Extract**:
- **Confidence level**: Strong/moderate/weak
- **Tone**: Optimistic/neutral/pessimistic
- **Defensiveness**: Evasive vs transparent

**Prompt Example**:
```
Analyze management tone in this earnings call transcript:
[Transcript]

Rate on 1-10 scale:
1. Overall confidence
2. Optimism about future
3. Transparency (vs evasiveness)
4. Concern level about challenges

Identify:
- Most confident statements
- Most concerning statements
- Changes from previous quarter's call
```

#### Keyword Frequency Analysis
**Track over time**:
- "Growth" mentions (bullish)
- "Challenge/difficult" mentions (bearish)
- "Invest/investing" (future focus)
- "Headwinds" (concerns)
- "Tailwinds" (optimism)

**Increasing frequency**:
- "Headwinds" increasing = deteriorating
- "Growth" increasing = improving

#### Question Topic Analysis
**What analysts ask about**:
- Repeated questions on same topic = concern
- New topics emerging = new risks/opportunities
- No questions on topic = less concern

### Use Cases

1. **Forward Guidance Extraction**: Inform estimates
2. **Management Quality Assessment**: Competence and honesty
3. **Risk Identification**: What keeps management up at night?
4. **Competitive Intelligence**: Market share, competitors mentioned
5. **Strategy Shifts**: New initiatives or pivots

### Signal Generation

**BULLISH Indicators**:
- Confident, optimistic tone
- Raising guidance
- Acceleration in key metrics
- "Investing for growth" language
- Minimal defensive responses
- Clear, specific answers

**BEARISH Indicators**:
- Hesitant, defensive tone
- Lowering guidance or removing guidance
- "Challenging environment" repetition
- Vague or evasive answers
- Multiple questions on same concern
- "One-time issues" explanations (often recurring)

**Red Flags**:
- Preparation vs spontaneity mismatch
- CFO and CEO contradictions
- Blaming external factors excessively
- Lack of specific metrics
- Avoiding certain topics

### Advanced FinLLM Techniques

**Comparative Analysis**:
```
Compare management tone across last 4 quarters:
Q1: [Transcript excerpt]
Q2: [Transcript excerpt]  
Q3: [Transcript excerpt]
Q4: [Transcript excerpt]

Identify:
1. Trend in confidence (improving/declining)
2. Recurring concerns
3. Promises made vs delivered
4. Strategy consistency
```

**Competitor Comparison**:
```
Compare earnings calls from [COMPANY] and top competitors:
[Multiple transcripts]

Analyze:
1. Who sounds more confident?
2. Who has better growth outlook?
3. Who addresses challenges better?
4. Competitive advantages mentioned
```

---

## 3. Top Gainers & Losers

### Description
Daily/weekly lists of stocks with largest percentage price changes. Market momentum indicator.

### Historical Data Required
**Real-time + 30-day history**

### Why Monitor?

1. **Momentum identification**: What's hot/cold
2. **Sector rotation**: Which sectors dominating
3. **Risk-on/risk-off**: Type of stocks moving
4. **Volatility spikes**: Unusual movements
5. **Short squeeze candidates**: Heavily shorted stocks spiking

### Use Cases

**If Your Stock Appears**:
- **Top Gainer**: Check why - news? Investigate sustainability
- **Top Loser**: Check why - news? Oversold bounce opportunity?

**Market Context**:
- Gainers = tech/growth? Risk-on sentiment
- Gainers = utilities/staples? Risk-off sentiment

### Signal Generation

**For Stocks on List**:
- Sudden appearance: Investigate catalyst
- Consecutive days: Momentum building
- Reversal from loser to gainer: Trend change?

---

## 4. Earnings Calendar

### Description
Upcoming earnings announcement dates and times.

### Historical Data Required
**Next quarter (forward-looking)**

### Why Critical?

1. **Volatility preparation**: Options pricing, position sizing
2. **Trading decisions**: Hold through earnings or not?
3. **Opportunity identification**: Pre/post earnings plays
4. **Calendar clustering**: Heavy earnings weeks

### Use Cases

**Before Earnings (1-2 weeks)**:
- Analyze historical earnings reactions
- Check earnings whisper numbers
- Assess sentiment trend
- Position sizing decisions

**Earnings Day**:
- Real-time price monitoring
- Immediate FinLLM analysis of results

**After Earnings**:
- Compare guidance to estimates
- Assess call transcript
- Evaluate market reaction (rational?)

### Signal Generation

**Pre-Earnings**:
- Strong sentiment + beat history = Hold or add
- Weak sentiment + miss history = Exit or reduce
- High volatility expected = Reduce size

**Post-Earnings**:
- Beat + positive guidance = Buy dips
- Beat + negative guidance = Sell rallies
- Miss + positive guidance = Neutral (wait)
- Miss + negative guidance = Exit

---

## 5. IPO Calendar

### Description
Upcoming initial public offerings (new stocks listing).

### Historical Data Required
**Next 90 days**

### Use Cases

1. **New opportunities**: Early-stage investments
2. **Sector trends**: What's coming to market?
3. **Market sentiment**: IPO volume = risk appetite
4. **Competitive landscape**: New competitors for existing holdings

### Signal Generation (Market-Level)
- Heavy IPO calendar = Bullish market sentiment
- Empty IPO calendar = Risk-off, bearish
- Tech IPOs dominating = Growth focus
- Defensive IPOs = Market uncertainty

---

# PART B: ALTERNATIVE DATA

## 6. Insider Transactions

### Description
Buying and selling of company stock by insiders (executives, directors, 10%+ owners).

### Historical Data Required
**Minimum**: 6 months  
**Recommended**: 12 months (1 year) ✅  
**Optimal**: 24 months (2 years)  
**Maximum useful**: 36 months (3 years)

### Why 12 Months?
1. **Pattern recognition**: Distinguish routine vs unusual
2. **Cluster identification**: Multiple insiders buying = strong signal
3. **Timing patterns**: Pre-earnings, post-earnings analysis
4. **Track record**: Do these insiders have good timing?
5. **Eliminate noise**: One-off transactions vs sustained activity

### Transaction Types

#### Buys (Bullish Signal)
**P - Purchase (Open Market)**:
- Most bullish (insider using own cash)
- Size matters (larger = stronger signal)

**Strong signal when**:
- Multiple insiders buying
- C-level executives (CEO, CFO)
- Significant dollar amounts

#### Sells (Neutral to Bearish)
**S - Sale**:
- Can be many reasons (diversification, tax, etc.)
- Less reliable than buys

**Bearish signal when**:
- Multiple insiders selling
- Unusually large sales
- Selling at market highs
- No concurrent buying

#### Neutral Transactions
**A - Award**: Stock-based compensation
**M - Exercise**: Option exercise
**G - Gift**: Personal gifts

**Less relevant for trading signals**

### Key Metrics

**Transaction Volume**:
- Number of buys vs sells
- Dollar value of buys vs sells

**Insider Participation**:
- % of insiders buying
- Which positions (CEO > Director)

**Purchase Size**:
- Relative to insider's wealth
- Relative to position size

**Timing**:
- After price drop (bottom fishing?)
- Before earnings (material info?)
- Pre-product launch (confidence?)

### Signal Strength

**VERY BULLISH** (Rare, Act Quickly):
- CEO/CFO open market buys > $500k
- Multiple C-level buys same week
- Buying after significant price drop
- First buy in 6+ months

**BULLISH**:
- Any C-level open market buy
- Multiple directors buying
- Sustained buying over weeks
- Buying while stock declining

**NEUTRAL**:
- Exercise + immediate sale (cashless exercise)
- Gifts, awards
- Single small sale

**BEARISH**:
- Multiple insiders selling large amounts
- CEO/CFO major sales
- Selling at new highs
- Zero insider buying for 6+ months

**VERY BEARISH** (Red Flag):
- Mass insider selling (many insiders same time)
- CEO selling majority of holdings
- Selling right before bad news (illegal but happens)

### Use Cases

1. **Contrarian Buy Signal**: Insiders buying during stock decline
2. **Confirmation**: Insiders buying confirms your bullish thesis
3. **Warning Sign**: No insider buying in year+ (lack of confidence)
4. **Sell Signal**: Unusual insider selling volume

### FinLLM Analysis

**Prompt Example**:
```
Analyze insider transaction pattern for [COMPANY] over 12 months:
[Transaction data: Date, Name, Title, Type, Shares, Price, Value]

Provide:
1. Overall pattern (bullish/neutral/bearish)
2. Notable transactions (size, timing, individuals)
3. Changes from historical pattern
4. Signal strength (1-10)
5. Potential reasons for activity
```

### Integration with Other Signals

**High Conviction Setups**:
- Technical oversold + Insider buying = Strong buy
- Earnings beat + Insider buying = Momentum buy
- Positive news + Insider buying = Confirmation buy

**Warning Setups**:
- Technical breakdown + Insider selling = Strong sell
- Negative news + Insider selling = Confirmation sell
- All-time high + Heavy insider selling = Take profits

---

## 7. Analytics - Fixed & Sliding Window

### Description
Technical analytics calculated over fixed or sliding time windows (SMA, EMA, RSI, ADX, etc.).

### Historical Data Required
**Minimum**: 30 days  
**Recommended**: 90 days  

### Use Cases
1. **Pre-calculated indicators**: Save computation time
2. **Backtesting**: Historical indicator values
3. **Validation**: Confirm your calculations

**Note**: You'll likely calculate these yourself from price data, so this is supplementary.

---

## 8. Realtime Bulk Quotes (Premium)

### Description
Real-time streaming prices for multiple symbols simultaneously.

### Use Cases
1. **Day trading**: Immediate price updates
2. **Market monitoring**: Watch multiple positions
3. **Execution**: Real-time bid/ask for order placement

### Signal Generation
- Use for execution timing, not signal generation
- Complements other signals with precise entry/exit

---

## 9. Options Data (Historical & Realtime)

### Description
Options chain data including strike prices, volumes, open interest, implied volatility.

### Historical Data Required
**Minimum**: 30 days  
**Recommended**: 90 days for patterns  

### Why Options Data?

#### Implied Volatility (IV)
- **High IV**: Market expects large move (earnings, events)
- **IV Percentile**: Current IV vs historical range
- **IV Rank**: Where current IV sits in range

**Use**:
- High IV before earnings = reduce position size (high risk)
- Low IV in stable stock = good time for long holds

#### Put/Call Ratio
- **P/C > 1**: More puts = bearish sentiment
- **P/C < 0.7**: More calls = bullish sentiment

**Extremes**:
- P/C > 1.5: Extreme fear (contrarian buy?)
- P/C < 0.5: Extreme greed (contrarian sell?)

#### Unusual Options Activity
- Sudden large call buying = bullish
- Sudden large put buying = bearish
- Large trades vs open interest = informed flow?

### Use Cases
1. **Volatility Expectations**: Size positions accordingly
2. **Sentiment Gauge**: Options flow shows positioning
3. **Event Risk**: IV spike = something coming
4. **Hedging**: Protective puts when bearish signals

### Signal Generation
- **Call volume spike + Price strength**: Momentum buy
- **Put volume spike + Price weakness**: Momentum sell
- **Unusual activity in far OTM calls**: Speculative bet (risky)

---

## 10. ETF Profile & Holdings

### Description
List of stocks held by ETFs and their weights.

### Use Cases

**Find Your Stock**:
- Which ETFs hold it?
- Large weight in ETF = correlated moves
- ETF inflows/outflows affect stock

**Sector/Industry Analysis**:
- What else is in the ETF?
- Peers for comparison
- Correlation opportunities

**Systematic Flows**:
- When ETF gets inflows → stock benefits
- When ETF rebalances → forced buying/selling

### Signal Generation
- Stock added to major ETF = Buying pressure
- Stock removed from major ETF = Selling pressure
- High ETF ownership = More volatile (passive flows)

---

# DATA INTEGRATION FRAMEWORK

## How Sentiment & Alternative Data Enhances Traditional Analysis

### Layer 1: Technical Analysis (Price Data)
**Provides**: Direction, momentum, support/resistance

### Layer 2: Fundamental Analysis (Financial Data)
**Provides**: Valuation, growth, financial health

### Layer 3: Sentiment Analysis (News, Transcripts)
**Provides**: Catalysts, risks, narrative

### Layer 4: Alternative Data (Insiders, Options)
**Provides**: Smart money positioning, expectations

---

## Signal Confluence Examples

### STRONG BUY Setup
1. **Technical**: Bullish breakout + Volume surge
2. **Fundamental**: EPS growth accelerating + Strong FCF
3. **Sentiment**: Positive news trend + Confident earnings call
4. **Alternative**: Multiple insider buys + Call volume spike

### STRONG SELL Setup
1. **Technical**: Breakdown below support + Declining volume
2. **Fundamental**: Revenue miss + Margin compression
3. **Sentiment**: Negative news cluster + Defensive earnings call
4. **Alternative**: Heavy insider selling + Put volume spike

### HOLD/WAIT Setup (Conflicting Signals)
1. **Technical**: Bullish
2. **Fundamental**: Bearish
3. **Sentiment**: Neutral
4. **Alternative**: No significant activity
→ **Wait for alignment before acting**

---

## Key Takeaways

### Must-Have Alternative Data
1. **News & Sentiments (90 days)** - Catalyst identification
2. **Insider Transactions (12 months)** - Smart money tracking
3. **Earnings Calendar** - Event management

### High-Value Add
4. **Earnings Call Transcripts (8 quarters)** - Management insight
5. **Earnings Estimates** - Forward expectations

### Optional/Advanced
6. **Options Data** - If trading options or advanced strategies
7. **Top Gainers/Losers** - Market pulse
8. **ETF Holdings** - Passive flow analysis

### Critical Insight
**Sentiment is leading, Price is lagging**
- News/insider activity happens before price moves
- Use sentiment to anticipate, price to confirm
- Biggest edge is in combining all layers

---

**Next**: [Signal Aggregation Methodology](./06_SIGNAL_AGGREGATION.md)
