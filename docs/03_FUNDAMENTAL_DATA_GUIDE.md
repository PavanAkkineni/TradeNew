# Fundamental Data Guide - Financial Analysis Foundation

## Overview
Fundamental data reveals a company's financial health, growth potential, and intrinsic value. This guide covers all financial statement APIs and their optimal usage for value-based trading signals.

---

## 1. Company Overview

### Description
Snapshot of company basics including sector, industry, market cap, P/E ratio, and key business metrics.

### Historical Data Required
**Current snapshot only** - Updated quarterly

### Why It's Critical
- **First step**: Understand what the company does
- **Sector context**: Compare with peers
- **Size classification**: Large/Mid/Small cap strategies differ
- **Dividend info**: Income vs growth categorization
- **Quick ratios**: P/E, PEG, P/B for initial screening

### Key Data Points
**Identity**:
- Name, Symbol, Exchange
- Sector, Industry
- Description (business model)

**Size & Metrics**:
- Market Capitalization (company size)
- Shares Outstanding
- 52-Week High/Low
- 50-day & 200-day Moving Averages

**Valuation Ratios**:
- P/E Ratio (Price-to-Earnings)
- PEG Ratio (P/E-to-Growth)
- Price-to-Book Ratio
- Price-to-Sales Ratio
- Dividend Yield

**Financial Health Snapshots**:
- EPS (Earnings Per Share)
- Beta (volatility vs market)
- Profit Margin
- ROE (Return on Equity)
- Revenue per Share

### Use Cases
1. **Initial Screening**: Filter investable universe
2. **Sector Allocation**: Industry-based strategies
3. **Peer Comparison**: Relative valuation
4. **Risk Assessment**: Beta and volatility metrics
5. **Dividend Strategy**: Yield and payout info

### Signal Generation
- **Low P/E + High PEG**: Potential undervaluation
- **ROE > 15%**: Efficient capital use
- **Dividend Yield > 3%**: Income opportunity
- **Beta < 1**: Defensive play
- **Beta > 1.5**: Aggressive growth

---

## 2. Income Statement (EARNINGS)

### Description
Quarterly and annual revenue, costs, and profit data. Shows company's profitability over time.

### Historical Data Required
**Minimum**: 8 quarters (2 years)  
**Recommended**: 20 quarters (5 years) ✅  
**Optimal**: 40 quarters (10 years)  

### Why 5 Years (20 Quarters)?
1. **Business cycles**: Captures full economic cycle
2. **Trend reliability**: Distinguish temporary from structural
3. **Growth calculations**: Multi-year CAGR (Compound Annual Growth Rate)
4. **Seasonal patterns**: Quarterly seasonality across years
5. **Margin trends**: Long-term profitability trajectory
6. **Competitive position**: Market share trends

### Key Line Items

#### Revenue Section
- **Total Revenue**: Top line growth
- **Cost of Revenue**: Direct production costs
- **Gross Profit**: Revenue - Cost of Revenue
- **Gross Profit Margin**: Gross Profit / Revenue

#### Operating Section
- **Operating Expenses**: R&D, SG&A, Marketing
- **Operating Income (EBIT)**: Earnings Before Interest & Tax
- **Operating Margin**: Operating Income / Revenue

#### Bottom Line
- **Net Income**: Final profit after all expenses
- **Net Margin**: Net Income / Revenue
- **EPS**: Earnings Per Share
- **Diluted EPS**: Accounts for options, convertibles

### Critical Metrics to Calculate

#### Growth Metrics
- **Revenue Growth (YoY)**: Quarter vs same quarter last year
- **Revenue Growth (QoQ)**: Quarter vs previous quarter
- **EPS Growth (YoY)**: Earnings momentum
- **Operating Income Growth**: Core business health

#### Profitability Metrics
- **Gross Margin %**: (Gross Profit / Revenue) × 100
- **Operating Margin %**: (Operating Income / Revenue) × 100
- **Net Margin %**: (Net Income / Revenue) × 100
- **EBITDA Margin**: Cash operating profitability

#### Efficiency Metrics
- **Revenue per Employee**: If employee count available
- **R&D as % Revenue**: Innovation investment
- **SG&A as % Revenue**: Overhead efficiency

### Use Cases
1. **Growth Stock Identification**: Consistent revenue/EPS growth
2. **Profitability Analysis**: Margin expansion/contraction
3. **Quality Assessment**: High margins = competitive advantage
4. **Earnings Surprises**: Compare actual vs estimates
5. **Trend Analysis**: Accelerating/decelerating growth

### Signal Generation

**BULLISH Signals**:
- Revenue growth accelerating (15%+ YoY)
- Margins expanding (shows pricing power)
- EPS growth > Revenue growth (improving efficiency)
- Operating leverage improving
- Beat earnings estimates consistently

**BEARISH Signals**:
- Revenue growth decelerating
- Margins compressing
- Revenue growing but profits shrinking
- Missing earnings estimates
- Unsustainable profit margins

### Optimal Analysis Period
- **Quarterly data**: Last 8 quarters for trends
- **Annual data**: Last 5 years for stability
- **Focus on**: Last 3 years for current trajectory

---

## 3. Balance Sheet

### Description
Snapshot of company's assets, liabilities, and equity. Shows financial health and stability.

### Historical Data Required
**Minimum**: 8 quarters (2 years)  
**Recommended**: 20 quarters (5 years) ✅  
**Optimal**: 40 quarters (10 years)

### Why 5 Years Critical?
1. **Debt trends**: Leverage increasing/decreasing
2. **Asset quality**: Accumulation of productive assets
3. **Working capital**: Operational efficiency trends
4. **Capital structure**: Equity vs debt financing evolution
5. **Financial flexibility**: Ability to weather downturns

### Key Sections

#### Assets
**Current Assets** (< 1 year):
- Cash and Cash Equivalents
- Short-term Investments
- Accounts Receivable
- Inventory
- **Total Current Assets**

**Non-Current Assets** (> 1 year):
- Property, Plant & Equipment (PP&E)
- Goodwill and Intangibles
- Long-term Investments
- **Total Non-Current Assets**

**TOTAL ASSETS**

#### Liabilities
**Current Liabilities** (< 1 year):
- Accounts Payable
- Short-term Debt
- Current Portion of Long-term Debt
- **Total Current Liabilities**

**Non-Current Liabilities** (> 1 year):
- Long-term Debt
- Deferred Tax Liabilities
- **Total Non-Current Liabilities**

**TOTAL LIABILITIES**

#### Equity
- Common Stock
- Retained Earnings
- **Total Shareholders Equity**

### Critical Ratios

#### Liquidity Ratios (Short-term health)
**Current Ratio** = Current Assets / Current Liabilities
- \> 2.0: Strong liquidity
- 1.0-2.0: Adequate
- < 1.0: Potential liquidity crisis

**Quick Ratio** = (Current Assets - Inventory) / Current Liabilities
- \> 1.0: Can meet short-term obligations
- < 1.0: May struggle with immediate debts

**Cash Ratio** = Cash / Current Liabilities
- \> 0.5: Very strong
- 0.2-0.5: Acceptable
- < 0.2: Potential issues

#### Solvency Ratios (Long-term health)
**Debt-to-Equity** = Total Debt / Total Equity
- < 0.5: Conservative (strong)
- 0.5-1.5: Moderate
- \> 2.0: Aggressive (risky)

**Debt-to-Assets** = Total Debt / Total Assets
- < 0.3: Low leverage
- 0.3-0.6: Moderate
- \> 0.6: High leverage

**Interest Coverage** = EBIT / Interest Expense (from income statement)
- \> 5: Safe
- 2-5: Moderate risk
- < 2: Distress warning

#### Efficiency Ratios
**Asset Turnover** = Revenue / Total Assets
- Higher = Better asset utilization
- Compare to industry average

**Inventory Turnover** = COGS / Average Inventory
- Higher = Better inventory management
- Industry-specific norms

#### Profitability Ratios
**Return on Assets (ROA)** = Net Income / Total Assets
- \> 5%: Good
- Measures asset efficiency

**Return on Equity (ROE)** = Net Income / Shareholders' Equity
- \> 15%: Excellent
- 10-15%: Good
- < 10%: Investigate why

**DuPont Analysis**: ROE = Net Margin × Asset Turnover × Equity Multiplier
- Breaks down ROE drivers

### Use Cases
1. **Financial Stability Assessment**: Can company survive downturns?
2. **Bankruptcy Risk**: Z-Score calculations
3. **Capital Structure**: Optimal debt/equity mix
4. **Working Capital Management**: Operational efficiency
5. **Asset Quality**: Productive vs unproductive assets

### Signal Generation

**BULLISH Signals**:
- Current Ratio improving and > 1.5
- Debt-to-Equity decreasing (deleveraging)
- ROE > 15% and stable
- Cash increasing as % of assets
- Working capital improving

**BEARISH Signals**:
- Current Ratio < 1.0 (liquidity crisis)
- Debt-to-Equity > 2.0 and rising
- Declining ROE
- Cash burn (cash decreasing)
- Rising inventory (potential obsolescence)

---

## 4. Cash Flow Statement

### Description
Actual cash movements in/out of business. Most reliable financial statement (harder to manipulate than income statement).

### Historical Data Required
**Minimum**: 8 quarters (2 years)  
**Recommended**: 20 quarters (5 years) ✅  
**Optimal**: 40 quarters (10 years)

### Why 5 Years Essential?
1. **Quality of earnings**: Cash flow vs accounting profit
2. **Sustainability**: Can company fund itself?
3. **Investment cycles**: CapEx patterns over time
4. **Dividend sustainability**: Cash available for distributions
5. **Financial flexibility**: Self-funding vs external capital

### Three Sections

#### Operating Cash Flow (OCF)
Cash from core business operations
- Net Income (starting point)
- \+ Depreciation & Amortization (non-cash expenses)
- Changes in Working Capital
- **= Cash from Operations**

#### Investing Cash Flow (ICF)
Cash from investments
- CapEx (Capital Expenditures) - usually negative
- Asset sales
- Acquisitions
- Investment purchases/sales
- **= Cash from Investing**

#### Financing Cash Flow (FCF)
Cash from financing activities
- Debt issuance/repayment
- Equity issuance/buybacks
- Dividend payments
- **= Cash from Financing**

**Net Change in Cash** = OCF + ICF + FCF

### Critical Metrics

#### Free Cash Flow (FCF)
**FCF** = Operating Cash Flow - Capital Expenditures

**Why critical?**
- Shows cash available for growth, dividends, buybacks
- Most important metric for valuation (DCF models)
- Indicates true financial health

**FCF Analysis**:
- **Positive & Growing**: Excellent - self-sustaining
- **Positive & Stable**: Good - mature business
- **Negative**: Investigate - growth phase or trouble?

#### Cash Flow Margins
**Operating Cash Flow Margin** = OCF / Revenue
- \> 15%: Excellent
- 10-15%: Good
- < 10%: Investigate

**Free Cash Flow Margin** = FCF / Revenue
- \> 10%: Excellent
- 5-10%: Good
- < 5%: Low quality

#### Quality Metrics

**Cash Conversion**
Cash from Operations / Net Income
- \> 1.0: High quality (generating more cash than profit)
- 0.8-1.0: Good
- < 0.8: Low quality (profits not converting to cash)

**Why important?**
- Net income can be manipulated (accruals)
- Cash is real
- Consistent ratio > 1.0 = high-quality earnings

#### Capital Efficiency

**CapEx Intensity** = CapEx / Revenue
- High ratio: Capital intensive (manufacturing, utilities)
- Low ratio: Asset-light (software, services)
- Trend matters: Rising = needs more investment to grow

**Cash Return on Invested Capital (CROIC)**
FCF / Invested Capital
- Measures cash generation efficiency
- \> 10%: Excellent

### Use Cases
1. **Earnings Quality**: Cash flow validates reported profits
2. **Dividend Safety**: OCF > Dividends paid = sustainable
3. **Growth Sustainability**: FCF funds growth without dilution
4. **Valuation**: DCF models use FCF projections
5. **Financial Stress Detection**: Negative FCF = potential problems

### Signal Generation

**BULLISH Signals**:
- FCF positive and growing
- OCF > Net Income (quality earnings)
- Increasing cash balance
- Decreasing CapEx needs (operating leverage)
- Buybacks from FCF (not debt)

**BEARISH Signals**:
- Negative FCF for multiple quarters
- OCF < Net Income (poor quality)
- Rising CapEx intensity
- Burning cash
- Paying dividends from debt (unsustainable)

### Advanced Analysis

**Cash Flow Patterns by Growth Stage**:

**Growth Stage**:
- Negative FCF (investing heavily)
- Rising OCF
- High CapEx
- *Acceptable if revenue growing fast*

**Mature Stage**:
- Strong positive FCF
- Stable OCF
- Moderate CapEx
- *Return cash via dividends/buybacks*

**Decline Stage**:
- Weak or negative OCF
- Decreasing FCF
- Cutting CapEx
- *Warning sign*

---

## 5. Earnings History

### Description
Historical quarterly earnings (actual EPS) vs analyst estimates. Shows beat/miss track record.

### Historical Data Required
**Minimum**: 8 quarters (2 years)  
**Recommended**: 12 quarters (3 years)  
**Optimal**: 20 quarters (5 years)

### Why This Matters
1. **Execution quality**: Consistent beats = good management
2. **Guidance quality**: Sandbagging vs over-promising
3. **Predictability**: Variance in estimates
4. **Market reaction**: Historical price response to earnings

### Key Data Points
- **Reported EPS**: Actual earnings per share
- **Estimated EPS**: Consensus analyst estimate
- **Surprise**: Actual - Estimate
- **Surprise %**: (Actual - Estimate) / Estimate × 100

### Analysis Metrics

**Beat Rate**
% of quarters where company beat estimates
- \> 75%: Excellent track record
- 50-75%: Good
- < 50%: Unreliable

**Average Surprise %**
Mean of surprise percentages
- \> +5%: Consistently sandbagging (good for traders)
- 0 to +5%: Meeting expectations
- Negative: Consistently missing (red flag)

**Consistency Score**
Standard deviation of surprises
- Low: Predictable
- High: Volatile, risky

### Use Cases
1. **Pre-earnings Trading**: Bet on historical beat pattern
2. **Post-earnings Analysis**: Normal vs abnormal reaction
3. **Management Credibility**: Do they deliver?
4. **Risk Assessment**: Earnings volatility

### Signal Generation
- **4+ consecutive beats**: Momentum signal (buy before earnings)
- **2+ consecutive misses**: Avoid or short
- **Improving trend**: Average surprise increasing
- **Deteriorating trend**: Average surprise decreasing

---

## 6. Earnings Estimates (EARNINGS_CALENDAR)

### Description
Forward-looking analyst estimates for upcoming quarters and years.

### Historical Data Required
**Current + Next 4 quarters** (1 year forward)  
**Current + Next 2 fiscal years**

### Why Forward-Looking Data?
- **Stock prices are forward-looking**: Trade on expectations
- **Estimate revisions**: Leading indicator of fundamentals
- **Valuation**: Forward P/E more relevant than trailing
- **Catalyst identification**: Major estimate changes

### Key Metrics

**EPS Estimates**:
- Current quarter estimate
- Next quarter estimate  
- Current year estimate
- Next year estimate

**Estimate Revisions**:
- Number of upward revisions (bullish)
- Number of downward revisions (bearish)
- Magnitude of revisions

**Analyst Coverage**:
- Number of analysts
- High/Low/Mean estimates
- Consensus estimate

### Use Cases
1. **Forward P/E Calculation**: Price / Next year EPS estimate
2. **Growth Rate Estimation**: This year vs next year growth
3. **Estimate Momentum**: Revisions trending up/down
4. **Surprise Potential**: Wide estimate range = higher uncertainty

### Signal Generation

**BULLISH Signals**:
- Upward estimate revisions
- Accelerating EPS growth (next year > this year)
- Narrowing estimate range (increasing confidence)
- Analyst upgrades

**BEARISH Signals**:
- Downward estimate revisions
- Decelerating EPS growth
- Widening estimate range (uncertainty)
- Analyst downgrades

---

## 7. Dividends (Corporate Actions)

### Description
Historical dividend payments including amount, ex-date, payment date.

### Historical Data Required
**Minimum**: 3 years  
**Recommended**: 5-10 years ✅  

### Why Long History?
1. **Dividend growth track record**: Consistency over cycles
2. **Aristocrat identification**: 25+ years of increases
3. **Sustainability analysis**: Payout through recessions
4. **Yield trends**: Historical yield ranges

### Key Metrics

**Dividend Yield**
Annual Dividend / Stock Price
- \> 4%: High yield
- 2-4%: Moderate
- < 2%: Low yield/growth focus

**Payout Ratio**
Dividends / Earnings (or FCF)
- < 50%: Conservative, sustainable
- 50-70%: Moderate
- \> 80%: Risk of cut

**Dividend Growth Rate**
- 5-year CAGR of dividend per share
- \> 10%: Excellent
- 5-10%: Good
- < 5%: Slow growth

**Consecutive Years of Increases**
- 25+: Dividend Aristocrat
- 10+: Dividend Achiever
- 5+: Dividend Contender

### Use Cases
1. **Income Investing**: High stable yields
2. **Dividend Growth Strategy**: Rising dividends
3. **Payout Sustainability**: Can they maintain it?
4. **Total Return Calculation**: Price + dividends

### Signal Generation
- **Dividend increase**: Bullish (confidence in cash flow)
- **Dividend cut**: Very bearish (financial stress)
- **Dividend initiation**: Bullish (maturing business)
- **Special dividend**: Neutral (one-time cash distribution)

---

## 8. Stock Splits (Corporate Actions)

### Description
Historical stock split events and ratios.

### Historical Data Required
**5-10 years** - To track split history

### Why It Matters
- **Price accessibility**: Splits make shares more affordable
- **Liquidity**: More shares trading
- **Historical price adjustment**: Need for accurate backtesting
- **Psychological signal**: Company confident in growth

### Types
- **Forward split**: 2-for-1, 3-for-1 (share price cut in half/third)
- **Reverse split**: 1-for-10 (often bearish - prop up price)

### Signal Generation
- **Forward split**: Mildly bullish (growing company)
- **Reverse split**: Bearish (avoiding delisting)

---

## 9. Shares Outstanding

### Description
Number of shares in circulation, tracked over time.

### Historical Data Required
**Quarterly for 5 years**

### Why Monitor?
- **Dilution**: Increasing shares = dilution
- **Buybacks**: Decreasing shares = shareholder friendly
- **EPS calculation**: EPS = Net Income / Shares
- **Ownership %**: Calculate stake percentage

### Signal Generation
- **Decreasing shares**: Bullish (buybacks, shareholder value)
- **Increasing shares**: Neutral to bearish (dilution from stock comp, offerings)

---

## Integration Strategy

### Priority Order for Initial Analysis

**Phase 1: Overview (Day 1)**
1. Company Overview
2. Latest quarter earnings (Income Statement)
3. Latest Balance Sheet
4. Latest Cash Flow

**Phase 2: Historical Trends (Day 2-3)**
5. Income Statement (5 years)
6. Balance Sheet (5 years)
7. Cash Flow (5 years)
8. Earnings History (3 years)

**Phase 3: Forward Looking (Day 4)**
9. Earnings Estimates
10. Earnings Calendar (next event)

**Phase 4: Shareholder Actions (Day 5)**
11. Dividends (if applicable)
12. Stock Splits history
13. Shares Outstanding trends

### Combined Fundamental Score

**Growth Score** (0-100):
- Revenue growth (30%)
- EPS growth (40%)
- FCF growth (30%)

**Quality Score** (0-100):
- Margins (30%)
- ROE (25%)
- Cash conversion (25%)
- Debt/Equity (20%)

**Value Score** (0-100):
- P/E vs sector (30%)
- P/FCF vs history (30%)
- PEG ratio (20%)
- Dividend yield (20%)

**Financial Health Score** (0-100):
- Current ratio (25%)
- Debt/Equity (25%)
- FCF positive (25%)
- Interest coverage (25%)

**Final Fundamental Signal** = Weighted average of 4 scores

---

## Key Takeaways

### Must-Have Data (Start Here)
1. **Company Overview** - Context
2. **Income Statement (5yr)** - Growth & profitability
3. **Balance Sheet (5yr)** - Financial health
4. **Cash Flow (5yr)** - Quality of earnings

### High-Value Add
5. **Earnings Estimates** - Forward looking
6. **Earnings History** - Track record

### Nice-to-Have
7. **Dividends** - If income focus
8. **Shares Outstanding** - Dilution tracking
9. **Stock Splits** - Historical context

### Critical Insight
**Cash Flow Quality** > **Reported Earnings**
- Companies can manipulate income statements
- Cash flow is harder to fake
- FCF is the ultimate health metric

---

**Next**: [Sentiment Data Guide](./04_SENTIMENT_DATA_GUIDE.md)
