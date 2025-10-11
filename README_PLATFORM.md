# 🚀 Trading Analytics Platform

A professional-grade trading analytics dashboard built with **FastAPI** and modern web technologies. Currently configured for **IBM** stock with plans to support multiple symbols.

## ✨ Features

### 📊 Technical Analysis Dashboard
- **Real-time price charts** with multiple timeframes
- **20+ Technical Indicators**:
  - RSI (Relative Strength Index)
  - MACD (Moving Average Convergence Divergence)
  - Moving Averages (SMA 20/50/200)
  - Bollinger Bands
  - Volume Analysis
  - Support & Resistance Levels
  - ATR (Average True Range)
  - Stochastic Oscillator

### 🎯 Intelligent Trade Signals
- **Multi-factor signal generation** combining:
  - Technical indicators (40% weight)
  - Fundamental analysis (30% weight)
  - Sentiment analysis (20% weight)
  - Insider trading data (10% weight)
- **Signal strength** from -100 (strong sell) to +100 (strong buy)
- **Confidence scoring** based on signal agreement
- **Entry/Exit points** with stop-loss and take-profit levels

### 📈 Data Integration
- **Alpha Vantage API** for price and fundamental data
- **EODHD API** for news and sentiment (optional)
- **Gemini AI** for advanced analysis (coming soon)

### 🎓 Educational Features
- **Interactive info buttons** on each indicator
- **Pop-up explanations** for trading concepts
- **Interpretation guides** for beginners

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- API Keys (see below)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd "c:/Users/admin/Documents/JOB APP/FastAPI/TradeSignal"

# Install dependencies
pip install -r requirements.txt
```

### 3. API Keys Setup

Create or edit `.env` file in the project root:

```env
# Required
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here

# Optional but recommended
GEMINI_API_KEY=your_gemini_key_here
EODHD_API_KEY=your_eodhd_key_here
```

Get your API keys:
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (Free)
- **Gemini**: https://makersuite.google.com/app/apikey (Free)
- **EODHD**: https://eodhd.com (Optional, paid)

### 4. Run the Application

**Option 1: Using the launcher script (Recommended)**
```bash
python run_app.py
```

**Option 2: Direct FastAPI command**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Dashboard

Open your browser and navigate to:
- **Dashboard**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 📁 Project Structure

```
TradeSignal/
│
├── app/                           # Backend application
│   ├── main.py                   # FastAPI main application
│   ├── technical_analysis.py     # Technical indicators calculator
│   ├── signal_generator.py       # Trade signal generation
│   ├── data_loader.py           # Data loading and management
│   ├── fundamental_analysis.py   # Financial analysis
│   └── sentiment_analysis.py     # Sentiment scoring
│
├── frontend/                      # Frontend application
│   ├── index.html                # Main dashboard page
│   └── static/
│       ├── css/style.css        # Modern dark theme styles
│       └── js/app.js            # Interactive dashboard logic
│
├── TechnicalAnalysis/            # Price data (IBM)
│   ├── Intraday/                # 5-minute bars
│   ├── Daily/                   # Daily adjusted prices
│   ├── Weekly/                  # Weekly adjusted prices
│   └── Monthly/                 # Monthly adjusted prices
│
├── FundamentalData/              # Financial statements
│   ├── company_overview_*.json  # Company metrics
│   ├── income_statement_*.json  # Revenue, earnings
│   ├── balance_sheet_*.json     # Assets, liabilities
│   └── cash_flow_*.json         # Cash flow statements
│
├── SentimentData/                # Market sentiment
│   ├── earnings_transcript_*.json # Earnings calls
│   ├── financial_news_*.json     # News articles
│   └── sentiment_scores_*.json   # Daily sentiment
│
└── AlternativeData/              # Alternative data sources
    └── insider_transactions_*.json # Insider trading

```

---

## 🎯 How It Works

### Technical Analysis Flow
1. **Data Loading**: Fetches IBM data from local JSON files
2. **Indicator Calculation**: Computes 20+ technical indicators
3. **Pattern Recognition**: Identifies trends and patterns
4. **Signal Generation**: Creates buy/sell/hold signals

### Signal Generation Logic
```
Final Signal = (Technical × 0.4) + (Fundamental × 0.3) + 
               (Sentiment × 0.2) + (Insider × 0.1)
```

**Signal Interpretation:**
- `> 50`: **STRONG BUY** 🟢
- `25 to 50`: **BUY** 🟢
- `10 to 25`: **WEAK BUY** 🟡
- `-10 to 10`: **HOLD** ⚪
- `-25 to -10`: **WEAK SELL** 🟡
- `-50 to -25`: **SELL** 🔴
- `< -50`: **STRONG SELL** 🔴

---

## 📊 Dashboard Features

### Main View
- **Stock Overview**: Current price, change, market cap, P/E ratio
- **Interactive Price Chart**: With moving averages overlay
- **Technical Indicators Grid**: 6 key indicator cards
- **Trade Signal Panel**: Action, strength, confidence, reasoning

### Educational Popups
Click any ℹ️ button to learn about:
- What the indicator means
- How to interpret values
- Trading strategies

### Navigation Tabs
- **Technical**: Complete technical analysis (Active)
- **Fundamental**: Financial metrics (Coming soon)
- **Sentiment**: News and social sentiment (Coming soon)
- **Trade Signals**: Comprehensive signals (Coming soon)

---

## 🛠️ API Endpoints

### Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard |
| `/api/health` | GET | Health check |
| `/api/symbols` | GET | Available symbols |
| `/api/technical/{symbol}` | GET | Technical analysis |
| `/api/signals/{symbol}` | GET | Trade signals |
| `/api/fundamental/{symbol}` | GET | Fundamental data |
| `/api/sentiment/{symbol}` | GET | Sentiment analysis |
| `/api/overview/{symbol}` | GET | Stock overview |
| `/api/education/{topic}` | GET | Educational content |

### Example API Call
```bash
curl http://localhost:8000/api/technical/IBM
```

---

## 🔧 Configuration

### Adding New Stocks
Currently, the platform is configured for IBM. To add more stocks:

1. **Fetch data** using the existing scripts in each folder
2. **Update symbol selector** in `frontend/index.html`
3. **Data will auto-load** when selected

### Customizing Weights
Edit signal weights in `app/signal_generator.py`:
```python
self.weights = {
    'technical': 0.40,    # 40%
    'fundamental': 0.30,  # 30%
    'sentiment': 0.20,    # 20%
    'insider': 0.10       # 10%
}
```

---

## 🚦 Current Status

### ✅ Completed
- FastAPI backend with all modules
- Technical analysis engine
- Signal generation system
- Modern responsive dashboard
- Educational popup system
- Data loading from existing JSON files

### 🔄 In Progress
- Gemini AI integration
- Multi-symbol support
- Real-time data updates

### 📋 Planned
- Portfolio management
- Backtesting engine
- Alert system
- Mobile app

---

## 📈 Trading Strategies

The platform implements several proven strategies:

### 1. **Trend Following**
- Uses SMA crossovers
- Confirms with MACD
- Volume validation

### 2. **Mean Reversion**
- RSI oversold/overbought
- Bollinger Band bounces
- Support/Resistance levels

### 3. **Momentum**
- MACD histogram
- Volume surges
- Price breakouts

### 4. **Smart Money**
- Insider buying clusters
- Institutional sentiment
- News catalyst detection

---

## 🎓 Educational Resources

The platform includes built-in education for:
- **RSI**: Momentum oscillator (0-100)
- **MACD**: Trend and momentum indicator
- **Moving Averages**: Trend identification
- **Volume**: Confirmation of price moves
- **Bollinger Bands**: Volatility and reversals
- **Support/Resistance**: Key price levels

---

## ⚠️ Disclaimer

**This platform is for educational and informational purposes only.**

- Not financial advice
- Past performance doesn't guarantee future results
- Always do your own research
- Consider consulting a financial advisor

---

## 🤝 Support

For issues or questions:
1. Check the documentation in `docs/` folder
2. Review API documentation at `/docs`
3. Verify data files are present
4. Ensure API keys are configured

---

## 📝 License

This project is for personal/educational use.

---

**Built with** ❤️ **using FastAPI, Chart.js, and modern web technologies**

Last Updated: October 2025
