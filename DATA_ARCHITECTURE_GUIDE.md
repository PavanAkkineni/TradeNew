# 📊 DATA ARCHITECTURE & COMPANY ADDITION GUIDE

## 🎯 **PURPOSE**
This guide explains the complete data architecture of the TradeCompass platform and provides step-by-step instructions for adding new companies (Microsoft, Capital One, Infosys) to the system.

---

## 📁 **CURRENT DATA STRUCTURE**

### **Root Directory Structure**
```
TradeCompass/
├── IBM/                          ← DATA FOLDER FOR IBM (Currently the only company)
│   ├── TechnicalAnalysis/        ← Price data & technical indicators
│   ├── FundamentalData/          ← Financial statements & company info
│   ├── SentimentData/            ← News, transcripts, sentiment scores
│   └── AlternativeData/          ← Insider transactions
│
├── app/                          ← Backend Python code
│   ├── data_loader.py            ← Loads data from IBM/ folder
│   ├── main.py                   ← FastAPI application
│   ├── technical_analysis.py     ← Calculates indicators
│   ├── fundamental_analysis.py   ← Analyzes financials
│   ├── sentiment_analysis.py     ← Analyzes sentiment
│   └── signal_generator.py       ← Generates trade signals
│
├── frontend/                     ← Web dashboard
│   ├── index.html                ← Main dashboard (has dropdown with IBM/AAPL/MSFT/GOOGL)
│   └── static/                   ← CSS, JavaScript, images
│
└── .env                          ← API keys configuration
```

---

## 🗂️ **DETAILED DATA FOLDER BREAKDOWN**

### **1. IBM/TechnicalAnalysis/** (Price Data)

**What's Inside:**
```
IBM/TechnicalAnalysis/
├── ibm_daily_adjusted_20251003_181415.json      ← Daily OHLCV data (100 days)
├── ibm_weekly_adjusted_20251003_181431.json     ← Weekly OHLCV data
├── ibm_monthly_adjusted_20251003_181446.json    ← Monthly OHLCV data
├── ibm_intraday_20251001_225947.json            ← 5-minute intraday data (30 days)
│
└── Scripts to fetch this data:
    ├── get_ibm_daily_adjusted.py
    ├── get_ibm_weekly_adjusted.py
    ├── get_ibm_monthly_adjusted.py
    └── get_ibm_intraday.py
```

**Data Source:** Alpha Vantage API
**API Function:** `TIME_SERIES_DAILY_ADJUSTED`, `TIME_SERIES_WEEKLY_ADJUSTED`, etc.
**What Platform Uses:** `ibm_daily_adjusted_*.json` (for charts and technical analysis)

**Sample Data Structure:**
```json
{
  "Meta Data": {
    "1. Information": "Daily Time Series with Splits and Dividend Events",
    "2. Symbol": "IBM"
  },
  "Time Series (Daily)": {
    "2025-10-03": {
      "1. open": "288.00",
      "2. high": "290.50",
      "3. low": "287.00",
      "4. close": "288.42",
      "5. adjusted close": "288.42",
      "6. volume": "3456789",
      "7. dividend amount": "0.00",
      "8. split coefficient": "1.0"
    }
  }
}
```

---

### **2. IBM/FundamentalData/** (Financial Statements)

**What's Inside:**
```
IBM/FundamentalData/
├── company_overview_20251003_182715.json        ← Company info, P/E, market cap, etc.
├── income_statement_20251003_182715.json        ← Revenue, profit, EPS (5 years)
├── balance_sheet_20251003_182715.json           ← Assets, liabilities, equity
├── cash_flow_20251003_182715.json               ← Operating, investing, financing cash flows
├── earnings_history_20251003_182715.json        ← Quarterly earnings & estimates
├── earnings_estimates_20251003_182715.json      ← Forward EPS estimates
├── dividends_20251003_182715.json               ← Dividend history
├── splits_20251003_182715.json                  ← Stock split history
├── shares_outstanding_20251003_182715.json      ← Share count over time
│
└── get_ibm_fundamental_data.py                  ← Script to fetch all fundamental data
```

**Data Source:** Alpha Vantage API
**API Functions:** `OVERVIEW`, `INCOME_STATEMENT`, `BALANCE_SHEET`, `CASH_FLOW`, `EARNINGS`, etc.
**What Platform Uses:** All files for fundamental analysis tab

**Sample Data (Company Overview):**
```json
{
  "Symbol": "IBM",
  "Name": "International Business Machines Corporation",
  "Sector": "Technology",
  "Industry": "Information Technology Services",
  "MarketCapitalization": "265000000000",
  "PERatio": "22.45",
  "DividendYield": "0.0345",
  "52WeekHigh": "295.00",
  "52WeekLow": "180.00"
}
```

---

### **3. IBM/SentimentData/** (News & Sentiment)

**What's Inside:**
```
IBM/SentimentData/
├── financial_news_20251003_185654.json          ← 90 days of news articles (12MB!)
├── sentiment_scores_20251003_185813.json        ← Daily sentiment scores (90 days)
├── earnings_transcript_2024Q1.json              ← Q1 2024 earnings call transcript
├── earnings_transcript_2024Q2.json              ← Q2 2024 earnings call transcript
├── earnings_transcript_2024Q3.json              ← Q3 2024 earnings call transcript
├── earnings_transcript_2024Q4.json              ← Q4 2024 earnings call transcript
├── earnings_transcript_2025Q1.json              ← Q1 2025 earnings call transcript
├── earnings_transcript_2025Q2.json              ← Q2 2025 earnings call transcript
├── earnings_transcript_2025Q3.json              ← Q3 2025 earnings call transcript
│
└── Scripts:
    ├── get_ibm_financial_news.py                ← Fetches news (EODHD API)
    ├── get_ibm_sentiment_scores.py              ← Fetches sentiment scores (EODHD API)
    └── get_ibm_earnings_transcripts.py          ← Fetches transcripts (Alpha Vantage API)
```

**Data Sources:** 
- **News & Sentiment Scores:** EODHD API (requires `EODHD_API_KEY`)
- **Earnings Transcripts:** Alpha Vantage API (uses `ALPHA_VANTAGE_API_KEY`)

**What Platform Uses:**
- `earnings_transcript_*.json` for sentiment analysis
- `financial_news_*.json` for news display
- `sentiment_scores_*.json` for sentiment trends

**Sample Sentiment Score:**
```json
{
  "IBM.US": [
    {
      "date": "2025-10-03",
      "normalized": 0.45,
      "count": 25,
      "polarity": 0.42,
      "pos": 0.65,
      "neg": 0.10,
      "neu": 0.25
    }
  ]
}
```

---

### **4. IBM/AlternativeData/** (Insider Transactions)

**What's Inside:**
```
IBM/AlternativeData/
├── insider_transactions_20251003_183809.json    ← 12+ months of insider trades (1.3MB)
└── get_ibm_insider_transactions.py              ← Script to fetch data
```

**Data Source:** Alpha Vantage API
**API Function:** `INSIDER_TRANSACTIONS`
**What Platform Uses:** Insider buying/selling analysis for alternative signals

**Sample Data:**
```json
{
  "data": [
    {
      "insider_name": "JOHN DOE",
      "title": "CEO",
      "transaction_date": "2025-09-15",
      "transaction_type": "P-Purchase",
      "securities_transacted": "10000",
      "security_price": "285.50",
      "total_value": "2855000"
    }
  ]
}
```

---

## 🔑 **API KEYS REQUIRED**

### **Current `.env` File:**
```env
ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### **For Complete Functionality:**
```env
# Required for Technical & Fundamental Data
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# Optional: For News & Sentiment (currently used but not required)
EODHD_API_KEY=your_eodhd_key

# Optional: For AI Analysis
GEMINI_API_KEY=your_gemini_key
```

### **Where to Get API Keys:**

1. **Alpha Vantage (FREE - Required)**
   - URL: https://www.alphavantage.co/support/#api-key
   - Limits: 25 requests/day, 5 requests/minute
   - Used for: Price data, fundamentals, earnings, insider transactions

2. **EODHD (Paid - Optional)**
   - URL: https://eodhd.com/
   - Used for: Financial news and sentiment scores
   - Note: Platform works without this (uses earnings transcripts for sentiment)

3. **Google Gemini (FREE - Optional)**
   - URL: https://makersuite.google.com/app/apikey
   - Used for: AI-powered analysis and insights

---

## 🔄 **HOW DATA FLOWS THROUGH THE PLATFORM**

### **Step-by-Step Data Flow:**

```
1. DATA COLLECTION (You run scripts manually)
   ├── Run: python IBM/TechnicalAnalysis/get_ibm_daily_adjusted.py
   ├── Run: python IBM/FundamentalData/get_ibm_fundamental_data.py
   ├── Run: python IBM/SentimentData/get_ibm_earnings_transcripts.py
   └── Result: JSON files saved in IBM/ subfolders

2. DATA LOADING (Automatic when server starts)
   ├── app/data_loader.py reads all JSON files from IBM/ folder
   ├── Parses and caches data in memory
   └── Makes data available to analysis modules

3. DATA ANALYSIS (When API endpoint called)
   ├── app/technical_analysis.py calculates RSI, MACD, etc.
   ├── app/fundamental_analysis.py analyzes financial ratios
   ├── app/sentiment_analysis.py extracts sentiment from transcripts
   └── app/signal_generator.py combines all signals

4. DATA DISPLAY (Frontend)
   ├── User opens http://localhost:8000
   ├── JavaScript calls API endpoints (e.g., /api/technical/IBM)
   ├── Backend returns processed data
   └── Charts and cards display on dashboard
```

### **Key File: `app/data_loader.py`**

This is the **MOST IMPORTANT** file for understanding data loading:

```python
# Lines 21-27: Defines where to look for data
self.folders = {
    'technical': os.path.join(self.root_dir, 'IBM', 'TechnicalAnalysis'),
    'fundamental': os.path.join(self.root_dir, 'IBM', 'FundamentalData'),
    'sentiment': os.path.join(self.root_dir, 'IBM', 'SentimentData'),
    'alternative': os.path.join(self.root_dir, 'IBM', 'AlternativeData')
}
```

**Notice:** Hardcoded to 'IBM' folder! This needs to change for multi-company support.

---

## ➕ **HOW TO ADD NEW COMPANIES**

### **Overview of Changes Needed:**

To add **Microsoft (MSFT)**, **Capital One (COF)**, and **Infosys (INFY)**, you need to:

1. ✅ Create folder structure for each company
2. ✅ Fetch data from APIs using modified scripts
3. ✅ Update `data_loader.py` to support multiple companies
4. ✅ Update frontend dropdown to include new companies
5. ✅ Update API endpoints to handle different symbols

---

## 📋 **STEP-BY-STEP GUIDE TO ADD NEW COMPANIES**

### **STEP 1: Create Folder Structure**

For each new company, create this structure:

```bash
# For Microsoft
TradeCompass/
└── MSFT/
    ├── TechnicalAnalysis/
    ├── FundamentalData/
    ├── SentimentData/
    └── AlternativeData/

# For Capital One
TradeCompass/
└── COF/
    ├── TechnicalAnalysis/
    ├── FundamentalData/
    ├── SentimentData/
    └── AlternativeData/

# For Infosys
TradeCompass/
└── INFY/
    ├── TechnicalAnalysis/
    ├── FundamentalData/
    ├── SentimentData/
    └── AlternativeData/
```

---

### **STEP 2: Copy and Modify Data Collection Scripts**

For each company, you need to:

#### **A. Technical Data (Price Data)**

**For Microsoft (MSFT):**
1. Copy `IBM/TechnicalAnalysis/get_ibm_daily_adjusted.py`
2. Rename to `MSFT/TechnicalAnalysis/get_msft_daily_adjusted.py`
3. Change inside the file:
   - Line 33: `'symbol': 'MSFT'` (instead of 'IBM')
   - Line 112: `filename = f"msft_daily_adjusted_{timestamp}.json"` (instead of ibm)

**Repeat for Weekly, Monthly, Intraday scripts**

#### **B. Fundamental Data**

**For Microsoft (MSFT):**
1. Copy `IBM/FundamentalData/get_ibm_fundamental_data.py`
2. Rename to `MSFT/FundamentalData/get_msft_fundamental_data.py`
3. Change:
   - Line 19: `SYMBOL = 'MSFT'` (instead of 'IBM')

#### **C. Sentiment Data**

**For Microsoft (MSFT):**
1. Copy `IBM/SentimentData/get_ibm_earnings_transcripts.py`
2. Rename to `MSFT/SentimentData/get_msft_earnings_transcripts.py`
3. Change:
   - Line 18: `SYMBOL = 'MSFT'` (instead of 'IBM')
   - Line 66: `filename = f"earnings_transcript_{quarter}.json"` (same - no change needed)

**If using EODHD for news:**
1. Copy news scripts and change `SYMBOL = 'MSFT.US'` (EODHD format)

#### **D. Alternative Data**

**For Microsoft (MSFT):**
1. Copy `IBM/AlternativeData/get_ibm_insider_transactions.py`
2. Rename to `MSFT/AlternativeData/get_msft_insider_transactions.py`
3. Change:
   - Line 18: `SYMBOL = 'MSFT'` (instead of 'IBM')

---

### **STEP 3: Fetch Data for New Companies**

Run the scripts for each company:

```bash
# For Microsoft
cd MSFT/TechnicalAnalysis
python get_msft_daily_adjusted.py

cd ../FundamentalData
python get_msft_fundamental_data.py

cd ../SentimentData
python get_msft_earnings_transcripts.py

cd ../AlternativeData
python get_msft_insider_transactions.py

# Repeat for COF and INFY
```

**Important Notes:**
- Alpha Vantage free tier: **25 requests/day, 5 requests/minute**
- Each fundamental data script makes ~9 API calls
- Wait 12 seconds between calls (built into scripts)
- You'll need **multiple days** to fetch all data for all companies
- Or get a premium Alpha Vantage subscription

---

### **STEP 4: Update `data_loader.py` (Code Changes Required)**

**Current Code (Hardcoded for IBM):**
```python
# Lines 21-27
self.folders = {
    'technical': os.path.join(self.root_dir, 'IBM', 'TechnicalAnalysis'),
    'fundamental': os.path.join(self.root_dir, 'IBM', 'FundamentalData'),
    'sentiment': os.path.join(self.root_dir, 'IBM', 'SentimentData'),
    'alternative': os.path.join(self.root_dir, 'IBM', 'AlternativeData')
}
```

**Needs to Change To (Dynamic):**
```python
def __init__(self, symbol='IBM'):
    self.symbol = symbol
    self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Dynamic folder paths based on symbol
    self.folders = {
        'technical': os.path.join(self.root_dir, symbol, 'TechnicalAnalysis'),
        'fundamental': os.path.join(self.root_dir, symbol, 'FundamentalData'),
        'sentiment': os.path.join(self.root_dir, symbol, 'SentimentData'),
        'alternative': os.path.join(self.root_dir, symbol, 'AlternativeData')
    }
```

**This requires updating:**
- `data_loader.py` constructor
- All calls to `DataLoader()` in other files
- API endpoints to pass symbol parameter

---

### **STEP 5: Update Frontend Dropdown**

**Current Frontend (index.html line 18-23):**
```html
<select id="symbolSelect" class="symbol-select">
    <option value="IBM">IBM</option>
    <option value="AAPL">AAPL</option>
    <option value="MSFT">MSFT</option>
    <option value="GOOGL">GOOGL</option>
</select>
```

**Update to:**
```html
<select id="symbolSelect" class="symbol-select">
    <option value="IBM">IBM - International Business Machines</option>
    <option value="MSFT">MSFT - Microsoft Corporation</option>
    <option value="COF">COF - Capital One Financial</option>
    <option value="INFY">INFY - Infosys Limited</option>
</select>
```

**JavaScript Needs Update:**
The dropdown is currently **non-functional** (displays but doesn't change data).
Need to add event listener to reload data when selection changes.

---

### **STEP 6: Update API Endpoints**

**Current API Endpoints:**
```python
@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str):
    # Currently works but needs data_loader update
```

These are already parameterized! But they create a new `DataLoader()` each time.
Need to update to `DataLoader(symbol)` after Step 4 changes.

---

## 📊 **DATA REQUIREMENTS SUMMARY**

### **Minimum Data Needed Per Company:**

| Data Type | Files Needed | API Calls | Size | Required? |
|-----------|--------------|-----------|------|-----------|
| **Price Data** | 1 daily JSON | 1 call | ~30KB | ✅ YES |
| **Company Overview** | 1 overview JSON | 1 call | ~3KB | ✅ YES |
| **Income Statement** | 1 JSON | 1 call | ~100KB | ✅ YES |
| **Balance Sheet** | 1 JSON | 1 call | ~170KB | ✅ YES |
| **Cash Flow** | 1 JSON | 1 call | ~140KB | ✅ YES |
| **Earnings** | 1 JSON | 1 call | ~33KB | ✅ YES |
| **Dividends** | 1 JSON | 1 call | ~20KB | ⚠️ Optional |
| **Splits** | 1 JSON | 1 call | ~1KB | ⚠️ Optional |
| **Shares Outstanding** | 1 JSON | 1 call | ~10KB | ⚠️ Optional |
| **Earnings Transcripts** | 8 JSONs (8 quarters) | 8 calls | ~400KB | ⚠️ Optional |
| **Insider Transactions** | 1 JSON | 1 call | ~1.3MB | ⚠️ Optional |
| **Financial News** | 1 JSON | N/A | ~12MB | ❌ Optional (EODHD) |
| **Sentiment Scores** | 1 JSON | N/A | ~8KB | ❌ Optional (EODHD) |

**Total API Calls (Alpha Vantage):** ~15 per company (for full data)
**For 3 Companies:** 45 API calls
**With Free Tier (25/day):** Takes 2 days to fetch all data

---

## 🚀 **SIMPLIFIED QUICK START FOR NEW COMPANIES**

### **Minimum Viable Data (6 API calls per company):**

To get the platform working with basic functionality:

1. ✅ Daily price data (1 call)
2. ✅ Company overview (1 call)
3. ✅ Income statement (1 call)
4. ✅ Balance sheet (1 call)
5. ✅ Cash flow (1 call)
6. ✅ Earnings history (1 call)

**This gives you:**
- ✅ Price charts
- ✅ Technical indicators (RSI, MACD, etc.)
- ✅ Basic fundamental ratios
- ✅ Trade signals
- ⚠️ Limited sentiment (only from available data)

**Skip for now:**
- Earnings transcripts (8 calls each)
- Insider transactions (if not needed)
- News/sentiment (requires EODHD)

---

## 🎯 **RECOMMENDED IMPLEMENTATION PLAN**

### **Phase 1: Prepare Structure (Day 1)**
1. Create folder structure for MSFT, COF, INFY
2. Copy and rename all Python scripts
3. Update SYMBOL variable in each script
4. Test one script to verify API key works

### **Phase 2: Fetch Minimal Data (Day 1-2)**
Using Alpha Vantage free tier (25 calls/day):

**Day 1:**
- MSFT: Daily, Overview, Income, Balance, Cash Flow, Earnings (6 calls)
- COF: Daily, Overview, Income, Balance, Cash Flow, Earnings (6 calls)
- INFY: Daily, Overview, Income, Balance, Cash Flow, Earnings (6 calls)
- **Total: 18 calls ✅ (within 25/day limit)**

**Day 2:**
- Optional: Fetch transcripts and insider data (if needed)

### **Phase 3: Code Updates (Day 2)**
1. Update `data_loader.py` to accept symbol parameter
2. Update all analysis modules
3. Update frontend dropdown functionality
4. Test with each symbol

### **Phase 4: Testing (Day 3)**
1. Load dashboard with IBM (verify still works)
2. Switch to MSFT (verify loads correctly)
3. Switch to COF (verify loads correctly)
4. Switch to INFY (verify loads correctly)

---

## ⚠️ **IMPORTANT CONSIDERATIONS**

### **Symbol Naming:**
- **IBM**: Works as-is
- **MSFT**: Microsoft - standard ticker
- **COF**: Capital One Financial - standard ticker
- **INFY**: Infosys Limited - traded on NYSE (not NSE)
  - Note: For NSE Infosys use 'INFY.NS' (if Alpha Vantage supports)
  - For NYSE Infosys use 'INFY'

### **Data Availability:**
- Alpha Vantage covers US stocks excellently
- INFY (Infosys) on NYSE should have full data
- If data missing, may need to use NSE ticker or different API

### **Rate Limits:**
- **Free Tier:** 25 calls/day, 5 calls/minute
- Scripts have built-in 12-second delays
- Fetching all data for 3 companies takes 2+ days
- Consider premium subscription if time-sensitive

### **File Naming Conventions:**
- Keep consistent: `{symbol}_daily_adjusted_{timestamp}.json`
- Scripts already generate timestamps automatically
- Latest file (by timestamp) is used by data_loader

---

## 🔍 **TROUBLESHOOTING GUIDE**

### **Problem: "No data found for symbol"**
**Solution:** 
1. Check folder exists: `MSFT/TechnicalAnalysis/`
2. Check JSON files exist in folder
3. Verify JSON file format matches IBM format
4. Check data_loader.py is looking in right folder

### **Problem: "API rate limit exceeded"**
**Solution:** 
1. Wait 1 minute between requests
2. Scripts have built-in delays
3. Track daily usage (25 max per day)
4. Consider premium API key

### **Problem: "Symbol not found"**
**Solution:**
1. Verify ticker symbol is correct
2. Check Alpha Vantage supports the symbol
3. Try alternate tickers (e.g., INFY vs INFY.NS)

### **Problem: "Dropdown doesn't switch companies"**
**Solution:**
This is expected - JavaScript not implemented yet.
Needs code update in `frontend/static/js/app.js`

---

## 📚 **REFERENCE: ALL API ENDPOINTS USED**

### **Alpha Vantage API Functions:**

1. **TIME_SERIES_DAILY_ADJUSTED** - Daily price data
2. **TIME_SERIES_WEEKLY_ADJUSTED** - Weekly price data
3. **TIME_SERIES_MONTHLY_ADJUSTED** - Monthly price data
4. **TIME_SERIES_INTRADAY** - Intraday 5-min data
5. **OVERVIEW** - Company overview and key metrics
6. **INCOME_STATEMENT** - Annual & quarterly income statements
7. **BALANCE_SHEET** - Annual & quarterly balance sheets
8. **CASH_FLOW** - Annual & quarterly cash flows
9. **EARNINGS** - Earnings history with estimates
10. **DIVIDENDS** - Dividend history
11. **SPLITS** - Stock split history
12. **SHARES_OUTSTANDING** - Quarterly share count
13. **EARNINGS_CALL_TRANSCRIPT** - Earnings call transcripts
14. **INSIDER_TRANSACTIONS** - Insider trading data
15. **EARNINGS_ESTIMATES** - Forward earnings estimates

**Documentation:** https://www.alphavantage.co/documentation/

---

## ✅ **CHECKLIST FOR ADDING NEW COMPANY**

Use this checklist for each new company:

### **MSFT (Microsoft) Checklist:**
- [ ] Create folder: `MSFT/TechnicalAnalysis/`
- [ ] Create folder: `MSFT/FundamentalData/`
- [ ] Create folder: `MSFT/SentimentData/`
- [ ] Create folder: `MSFT/AlternativeData/`
- [ ] Copy & modify: `get_msft_daily_adjusted.py`
- [ ] Copy & modify: `get_msft_fundamental_data.py`
- [ ] Copy & modify: `get_msft_earnings_transcripts.py` (optional)
- [ ] Copy & modify: `get_msft_insider_transactions.py` (optional)
- [ ] Run: `python get_msft_daily_adjusted.py`
- [ ] Run: `python get_msft_fundamental_data.py`
- [ ] Verify: JSON files created in folders
- [ ] Verify: File sizes match expected (check IBM for comparison)
- [ ] Test: Load data in dashboard (after code updates)

### **COF (Capital One) Checklist:**
- [ ] Same as MSFT, replace with COF

### **INFY (Infosys) Checklist:**
- [ ] Same as MSFT, replace with INFY
- [ ] Verify: INFY ticker works (might need INFY.NS for NSE)

---

## 🎓 **LEARNING RESOURCES**

### **Understanding the Data:**
- **OHLCV**: Open, High, Low, Close, Volume
- **Adjusted Close**: Accounts for splits and dividends
- **Fundamental Ratios**: P/E, ROE, Debt/Equity calculated from statements
- **Sentiment Scores**: -1 (negative) to +1 (positive)

### **API Documentation:**
- Alpha Vantage: https://www.alphavantage.co/documentation/
- EODHD: https://eodhd.com/financial-apis/
- Google Gemini: https://ai.google.dev/docs

---

## 📞 **SUMMARY**

### **What You Have Now:**
- ✅ Complete data for IBM (all 4 data types)
- ✅ Working dashboard for IBM
- ✅ All scripts to fetch data

### **What You Need to Do:**
1. Create folder structure for MSFT, COF, INFY
2. Copy and modify Python scripts (change SYMBOL variable)
3. Run scripts to fetch data (takes 2 days with free API)
4. Update code to support multiple symbols
5. Update frontend dropdown functionality

### **Estimated Time:**
- **Manual Setup**: 2-3 hours (creating folders, copying scripts)
- **Data Fetching**: 2 days (due to API rate limits)
- **Code Updates**: 4-6 hours (updating data_loader and frontend)
- **Testing**: 2-3 hours
- **Total**: ~3-4 days

### **Key Files to Modify:**
1. `app/data_loader.py` - Make symbol dynamic
2. `app/main.py` - Update DataLoader instantiation
3. `frontend/index.html` - Update dropdown options
4. `frontend/static/js/app.js` - Add dropdown change handler

---

## 🚀 **NEXT STEPS**

1. **Read this document carefully**
2. **Verify API key** in `.env` file
3. **Create folder structure** for new companies
4. **Copy and modify scripts** (change SYMBOL)
5. **Start fetching data** (6 calls per company minimum)
6. **Wait for all data** (2 days with free tier)
7. **Ask for code changes** (data_loader.py, frontend, etc.)

---

**Document Version:** 1.0
**Last Updated:** October 11, 2025
**Author:** TradeCompass Development Team

---

**Questions?** Review this document and identify specific sections where you need clarification!
