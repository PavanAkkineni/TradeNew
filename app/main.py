"""
Trading Analytics Platform - Main FastAPI Application
"""
# Load environment variables first, before any other imports
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
import json
import os
from datetime import datetime

# Import our modules
from app.technical_analysis import TechnicalAnalyzer
from app.signal_generator import SignalGenerator
from app.data_loader import DataLoader
from app.fundamental_analysis import FundamentalAnalyzer
from app.sentiment_analysis import SentimentAnalyzer
from app.gemini_analyzer import GeminiAnalyzer
from app.market_data_aggregator import MarketDataAggregator
from app.portfolio_recommender import PortfolioRecommender

# Import auth and database modules
from app.database import get_db, init_db, User, UserProfile
from app import auth
from app.voice_form_filler import router as voice_router
from app.voice_assistant_tts import router as voice_assistant_router

app = FastAPI(title="Trading Analytics Platform", version="1.0.0")

# Include routers
app.include_router(voice_router)
app.include_router(voice_assistant_router)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("Database initialized!")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Initialize components
data_loader = DataLoader()
technical_analyzer = TechnicalAnalyzer()
signal_generator = SignalGenerator()
fundamental_analyzer = FundamentalAnalyzer()
sentiment_analyzer = SentimentAnalyzer()
gemini_analyzer = GeminiAnalyzer()
market_data_aggregator = MarketDataAggregator()  # Component 2: Market Data Aggregation Engine
portfolio_recommender = PortfolioRecommender()   # Component 3: Portfolio Recommendation Engine

# Security
security = HTTPBearer()

# Request/Response Models
class StockRequest(BaseModel):
    symbol: str = "IBM"
    
class TechnicalIndicators(BaseModel):
    symbol: str
    current_price: float
    price_change: float
    price_change_percent: float
    volume: int
    sma_20: float
    sma_50: float
    sma_200: float
    ema_12: float
    ema_26: float
    rsi: float
    macd: Dict[str, float]
    bollinger_bands: Dict[str, float]
    support_resistance: Dict[str, List[float]]
    volume_analysis: Dict[str, Any]
    trend: str
    
class TradeSignal(BaseModel):
    signal: str  # BUY, SELL, HOLD
    strength: float  # -100 to 100
    confidence: float  # 0 to 100
    reasoning: List[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    entry_price: float
    stop_loss: float
    take_profit: List[float]  # Multiple targets
    timeframe: str

@app.get("/")
async def root():
    """Serve the landing page"""
    return FileResponse("frontend/landing.html")

@app.get("/dashboard")
async def dashboard():
    """Serve the main dashboard"""
    return FileResponse("frontend/index.html")

@app.get("/landing")
async def landing():
    """Serve the landing page"""
    return FileResponse("frontend/landing.html")

@app.get("/login.html")
async def login_page():
    """Serve the login page"""
    return FileResponse("frontend/login.html")

@app.get("/signup.html")
async def signup_page():
    """Serve the signup page"""
    return FileResponse("frontend/signup.html")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/symbols")
async def get_available_symbols():
    """Get list of available symbols with data"""
    symbols = data_loader.get_available_symbols()
    return {"symbols": symbols, "default": "IBM"}

@app.get("/api/technical/{symbol}")
async def get_technical_analysis(symbol: str = "IBM"):
    """
    Get comprehensive technical analysis for a symbol
    """
    try:
        # Load price data
        price_data = data_loader.load_price_data(symbol)
        
        if price_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate all technical indicators
        indicators = technical_analyzer.calculate_all_indicators(price_data)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "chart_data": technical_analyzer.prepare_chart_data(price_data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/signals/{symbol}")
async def get_trade_signals(symbol: str = "IBM"):
    """
    Generate comprehensive trade signals based on all data types
    """
    try:
        # Load all data types
        price_data = data_loader.load_price_data(symbol)
        fundamental_data = data_loader.load_fundamental_data(symbol)
        sentiment_data = data_loader.load_sentiment_data(symbol)
        insider_data = data_loader.load_insider_data(symbol)
        
        # Calculate indicators from each analysis type
        if not price_data.empty:
            tech_indicators = technical_analyzer.calculate_all_indicators(price_data)
        else:
            tech_indicators = {}
        
        fund_metrics = fundamental_analyzer.analyze(fundamental_data) if fundamental_data else None
        sent_score = sentiment_analyzer.analyze(sentiment_data) if sentiment_data else None
        
        # Generate comprehensive trade signal
        signal = signal_generator.generate_signal(
            technical=tech_indicators,
            fundamental=fund_metrics,
            sentiment=sent_score,
            insider=insider_data
        )
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "signal": signal
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fundamental/{symbol}")
async def get_fundamental_analysis(symbol: str = "IBM"):
    """
    Get fundamental analysis for a symbol
    """
    try:
        fundamental_data = data_loader.load_fundamental_data(symbol)
        
        if not fundamental_data:
            raise HTTPException(status_code=404, detail=f"No fundamental data found for {symbol}")
        
        analysis = fundamental_analyzer.analyze(fundamental_data)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sentiment/{symbol}")
async def get_sentiment_analysis(symbol: str = "IBM"):
    """
    Get sentiment analysis for a symbol
    """
    try:
        sentiment_data = data_loader.load_sentiment_data(symbol)
        
        if not sentiment_data:
            raise HTTPException(status_code=404, detail=f"No sentiment data found for {symbol}")
        
        analysis = sentiment_analyzer.analyze(sentiment_data)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/overview/{symbol}")
async def get_stock_overview(symbol: str = "IBM"):
    """
    Get complete overview including price, volume, and key metrics
    """
    try:
        price_data = data_loader.load_price_data(symbol)
        company_info = data_loader.load_company_overview(symbol)
        
        # Get latest price info
        if not price_data.empty:
            latest_price = technical_analyzer.get_latest_price_info(price_data)
        else:
            latest_price = {'price': 0, 'open': 0, 'high': 0, 'low': 0, 'volume': 0}
        
        # Get key stats
        key_stats = {
            "market_cap": company_info.get("MarketCapitalization", 0),
            "pe_ratio": company_info.get("PERatio", 0),
            "dividend_yield": company_info.get("DividendYield", 0),
            "eps": company_info.get("EPS", 0),
            "beta": company_info.get("Beta", 0),
            "52_week_high": company_info.get("52WeekHigh", 0),
            "52_week_low": company_info.get("52WeekLow", 0),
            "shares_outstanding": company_info.get("SharesOutstanding", 0)
        }
        
        return {
            "symbol": symbol,
            "name": company_info.get("Name", symbol),
            "sector": company_info.get("Sector", "N/A"),
            "industry": company_info.get("Industry", "N/A"),
            "exchange": company_info.get("Exchange", "N/A"),
            "current_price": latest_price,
            "key_stats": key_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/fetch-data")
async def fetch_new_data(request: StockRequest):
    """
    Fetch fresh data for a new symbol from APIs
    """
    try:
        # This will trigger data fetching for a new symbol
        result = data_loader.fetch_data_for_symbol(request.symbol)
        
        if result["success"]:
            return {
                "success": True,
                "message": f"Data fetched successfully for {request.symbol}",
                "data_types": result["data_types"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-analysis/{symbol}")
async def get_ai_analysis(symbol: str = "IBM"):
    """
    Get AI-powered analysis using Gemini
    """
    try:
        # Load all data types
        price_data = data_loader.load_price_data(symbol)
        fundamental_data = data_loader.load_fundamental_data(symbol)
        sentiment_data = data_loader.load_sentiment_data(symbol)
        
        # Calculate indicators
        tech_indicators = technical_analyzer.calculate_all_indicators(price_data) if not price_data.empty else {}
        
        # Get AI analysis
        ai_analysis = gemini_analyzer.analyze_comprehensive({
            'technical': tech_indicators,
            'fundamental': fundamental_data,
            'sentiment': sentiment_data
        })
        
        # Get AI trade recommendation
        ai_recommendation = gemini_analyzer.generate_trade_recommendation(
            tech_indicators,
            fundamental_data,
            sentiment_data
        )
        
        # Get market commentary
        commentary = gemini_analyzer.market_commentary(symbol)
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "analysis": ai_analysis,
            "recommendation": ai_recommendation,
            "market_commentary": commentary
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trading-expert/{symbol}")
async def get_trading_expert_analysis(symbol: str = "IBM"):
    """
    Get comprehensive trading expert analysis combining computed signals with AI insights
    """
    try:
        # Load price data and calculate technical indicators
        price_data = data_loader.load_price_data(symbol)
        
        if price_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")
        
        # Calculate technical indicators
        tech_indicators = technical_analyzer.calculate_all_indicators(price_data)
        
        # Generate computed signal using mathematical model
        computed_signal = signal_generator.generate_signal(
            technical=tech_indicators,
            fundamental=None,  # Focus on technical for now
            sentiment=None,
            insider=None
        )
        
        # Get individual signal breakdown (mock for now - you can implement this in signal_generator)
        individual_signals = {
            "rsi": {
                "signal": "OVERBOUGHT" if tech_indicators.get('rsi', 50) > 70 else "OVERSOLD" if tech_indicators.get('rsi', 50) < 30 else "NEUTRAL",
                "weight": "25%",
                "contribution": f"{tech_indicators.get('rsi', 50):.2f}"
            },
            "macd": {
                "signal": "BULLISH" if tech_indicators.get('macd', {}).get('histogram', 0) > 0 else "BEARISH",
                "weight": "20%", 
                "contribution": f"{tech_indicators.get('macd', {}).get('histogram', 0):.3f}"
            },
            "moving_averages": {
                "signal": "UPTREND" if tech_indicators.get('current_price', 0) > tech_indicators.get('sma', {}).get('sma_20', 0) else "DOWNTREND",
                "weight": "18%",
                "contribution": f"Price vs SMA20: {((tech_indicators.get('current_price', 0) / max(tech_indicators.get('sma', {}).get('sma_20', 1), 1) - 1) * 100):.2f}%"
            },
            "volume": {
                "signal": tech_indicators.get('volume_analysis', {}).get('signal', 'NEUTRAL').upper(),
                "weight": "15%",
                "contribution": f"{tech_indicators.get('volume_analysis', {}).get('ratio', 1):.2f}x"
            },
            "bollinger_bands": {
                "signal": "OVERBOUGHT" if tech_indicators.get('bollinger_bands', {}).get('percent_b', 0.5) > 0.8 else "OVERSOLD" if tech_indicators.get('bollinger_bands', {}).get('percent_b', 0.5) < 0.2 else "NEUTRAL",
                "weight": "12%",
                "contribution": f"%B: {tech_indicators.get('bollinger_bands', {}).get('percent_b', 0.5):.3f}"
            },
            "support_resistance": {
                "signal": "AT_RESISTANCE" if any(abs(tech_indicators.get('current_price', 0) - r) < 2 for r in tech_indicators.get('support_resistance', {}).get('resistance', [])) else "AT_SUPPORT" if any(abs(tech_indicators.get('current_price', 0) - s) < 2 for s in tech_indicators.get('support_resistance', {}).get('support', [])) else "NEUTRAL",
                "weight": "10%",
                "contribution": f"Next R: ${tech_indicators.get('support_resistance', {}).get('resistance', [0])[0] if tech_indicators.get('support_resistance', {}).get('resistance') else 'N/A'}"
            }
        }
        
        # Get Gemini trading expert analysis
        expert_analysis = gemini_analyzer.trading_expert_analysis(
            tech_indicators, 
            computed_signal, 
            individual_signals
        )
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "computed_signal": {
                "action": computed_signal.get('signal', 'HOLD'),
                "strength": computed_signal.get('strength', 0),
                "confidence": computed_signal.get('confidence', 50),
                "reasoning": computed_signal.get('reasoning', [])
            },
            "individual_signals": individual_signals,
            "expert_analysis": expert_analysis,
            "technical_indicators": tech_indicators
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Portfolio Profile Model
class PortfolioProfile(BaseModel):
    investment_capital: float
    target_amount: float
    time_horizon: int
    risk_appetite: str

@app.post("/api/portfolio-profile")
async def submit_portfolio_profile(profile: PortfolioProfile):
    """
    Receive and validate user's investment profile
    Returns the profile data for confirmation
    """
    try:
        # Validate inputs
        if profile.investment_capital <= 0:
            raise HTTPException(status_code=400, detail="Investment capital must be positive")
        
        if profile.target_amount <= profile.investment_capital:
            raise HTTPException(status_code=400, detail="Target amount must be greater than investment capital")
        
        if profile.time_horizon <= 0:
            raise HTTPException(status_code=400, detail="Time horizon must be positive")
        
        if profile.risk_appetite not in ['conservative', 'moderate', 'aggressive']:
            raise HTTPException(status_code=400, detail="Invalid risk appetite")
        
        # Calculate some basic metrics
        required_return = ((profile.target_amount / profile.investment_capital) ** (1 / profile.time_horizon) - 1) * 100
        
        # Return profile with calculations
        return {
            "investment_capital": profile.investment_capital,
            "target_amount": profile.target_amount,
            "time_horizon": profile.time_horizon,
            "risk_appetite": profile.risk_appetite,
            "required_annual_return": round(required_return, 2),
            "status": "success",
            "message": "Portfolio profile received successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing portfolio profile: {str(e)}")

@app.get("/api/market-data")
async def get_market_data():
    """
    Component 2: Market Data Aggregation Engine
    
    Fetches comprehensive market data from multiple sources:
    - Economic Indicators (FRED API): CPI, Fed Funds Rate, GDP, Unemployment
    - Market Performance (Alpha Vantage/Finnhub): S&P 500, VIX, Treasury, Gold, VNQ
    - Market Sentiment (NewsAPI): Recent headlines about stock market and economy
    
    This is a pure data aggregation endpoint - no interpretation, just facts.
    """
    try:
        market_data = market_data_aggregator.aggregate_all_data(use_cache=False)
        return market_data
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error aggregating market data: {str(e)}"
        )

@app.get("/api/market-data/economic")
async def get_economic_indicators():
    """
    Get only economic indicators (FRED API data)
    """
    try:
        indicators = market_data_aggregator.fetch_economic_indicators()
        return {
            'timestamp': datetime.now().isoformat(),
            'economic_indicators': indicators
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching economic indicators: {str(e)}"
        )

@app.get("/api/market-data/performance")
async def get_market_performance():
    """
    Get only market performance metrics (Alpha Vantage/Finnhub data)
    """
    try:
        performance = market_data_aggregator.fetch_market_performance()
        return {
            'timestamp': datetime.now().isoformat(),
            'market_performance': performance
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market performance: {str(e)}"
        )

@app.get("/api/market-data/sentiment")
async def get_market_sentiment(query: str = "stock market economy"):
    """
    Get only market sentiment (NewsAPI headlines)
    """
    try:
        sentiment = market_data_aggregator.fetch_market_sentiment(query=query)
        return {
            'timestamp': datetime.now().isoformat(),
            'market_sentiment': sentiment
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching market sentiment: {str(e)}"
        )

@app.post("/api/portfolio-recommendation")
async def generate_portfolio_recommendation(profile: PortfolioProfile):
    """
    Component 3: Generate AI-powered portfolio recommendation
    
    Combines user profile with current market data and uses Gemini AI
    to generate personalized portfolio allocation and justification.
    
    Request body:
    {
        "investment_capital": 50000,
        "target_amount": 100000,
        "time_horizon": 7,
        "risk_appetite": "moderate"
    }
    
    Returns:
    {
        "success": true,
        "recommendation": {
            "portfolio_allocation": {...},
            "justification": {...},
            "expected_returns": {...}
        },
        "market_data_used": {...},
        "timestamp": "..."
    }
    """
    try:
        # Get current market data (fresh data, no cache)
        market_data = market_data_aggregator.aggregate_all_data(use_cache=False)
        
        # Convert profile to dict
        user_profile = {
            'investment_capital': profile.investment_capital,
            'target_amount': profile.target_amount,
            'time_horizon': profile.time_horizon,
            'risk_appetite': profile.risk_appetite
        }
        
        # Generate recommendation using Gemini
        result = portfolio_recommender.generate_portfolio_recommendation(
            user_profile=user_profile,
            market_data=market_data
        )
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['market_data_timestamp'] = market_data.get('timestamp')
        result['market_data_used'] = {
            'economic_summary': {
                'inflation': market_data.get('economic_indicators', {}).get('inflation_rate', {}).get('value'),
                'fed_rate': market_data.get('economic_indicators', {}).get('federal_funds_rate', {}).get('value'),
                'gdp': market_data.get('economic_indicators', {}).get('gdp_growth_rate', {}).get('value')
            },
            'market_summary': {
                'sp500': market_data.get('market_performance', {}).get('sp500', {}).get('current_price'),
                'vix': market_data.get('market_performance', {}).get('vix', {}).get('current_price')
            }
        }
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating portfolio recommendation: {str(e)}"
        )

@app.get("/api/education/{topic}")
async def get_educational_content(topic: str):
    """
    Get educational content for various trading concepts
    """
    educational_content = {
        "rsi": {
            "title": "Relative Strength Index (RSI) - Momentum Indicator",
            "description": "RSI is like a speedometer for your car, but instead of measuring miles per hour, it measures how fast and how strongly a stock's price is moving. Just like you wouldn't want to drive too fast or too slow, RSI helps you see if a stock price has been moving too much, too quickly in one direction. It gives you a simple number between 0 and 100 to understand the stock's current momentum.",
            "what_it_is": "RSI is calculated by comparing the average of recent price gains to the average of recent price losses over the past 14 trading days (about 3 weeks). The formula gives you a score: If a stock only went up for 14 days straight, RSI would be 100. If it only went down, RSI would be 0. Most of the time, it's somewhere in between. Created by technical analyst J. Welles Wilder in 1978, it's one of the most widely used and trusted momentum indicators by professional traders, investors, and algorithms worldwide.",
            "why_important": "RSI is important because it helps you avoid two costly mistakes: (1) Buying a stock that's already risen too much and is likely to drop (buying high), and (2) Selling a stock that's already fallen too much and is likely to bounce back (selling low). Think of it as an early warning system that tells you when emotions might be driving the price too far from its normal pattern. When everyone is rushing to buy and pushing the price up rapidly (high RSI), it often means the enthusiasm won't last. When everyone is panicking and selling (low RSI), it often means the fear is overdone. RSI helps you stay calm and make rational decisions when others are emotional.",
            "how_to_read": [
                "🔴 RSI above 70: Stock is 'overbought' - Like a car engine that's been revving too high for too long. Many buyers have already bought, so there might not be enough new buyers to push the price higher. Consider taking profits or waiting for a better entry.",
                "🟢 RSI below 30: Stock is 'oversold' - Like finding a quality item on clearance sale. So many people have sold that there aren't many sellers left. Often a good time to start looking for buying opportunities, especially in quality stocks.",
                "🟡 RSI between 30-70: Normal trading range - The stock is in its 'healthy' zone. No extreme signals. Price movement is balanced between buyers and sellers.",
                "⚪ RSI around 50: Perfectly balanced - Equal strength between buyers and sellers. No momentum in either direction. Like a tug-of-war where both teams are equally strong.",
                "📈 RSI rising from below 50: Building bullish momentum - Buyers are gaining strength.",
                "📉 RSI falling from above 50: Building bearish momentum - Sellers are gaining control."
            ],
            "signal_contribution": "25%",
            "contribution_explanation": "RSI contributes 25% (the largest share) to our final trading signal because momentum is absolutely crucial for timing your entries and exits. It's like surfing - you want to catch the wave at the right time. A high RSI value (above 70) sends a caution signal, reducing our buy recommendation. A low RSI value (below 30) sends a positive signal, increasing our buy recommendation. The RSI also helps us determine if other signals are reliable - for example, if fundamentals look good but RSI is above 80, we might suggest waiting for a better entry point.",
            "beginner_tip": "Think of RSI like a rubber band around your wrist. When you stretch it too far in one direction (RSI above 70 or below 30), it wants to snap back to its normal position (around 50). This doesn't mean it will snap back immediately - sometimes the rubber band can stay stretched for a while - but it gives you a heads up that a reversal could be coming. Also remember: In strong uptrends, RSI can stay above 70 for extended periods (the 'rubber band' is stronger). In strong downtrends, it can stay below 30 for a long time. Always use RSI together with other indicators and overall trend direction.",
            "trading_strategy": "Conservative approach: When RSI is above 70, avoid buying and consider taking profits if you own the stock. Wait for RSI to drop back below 70 before considering new purchases. When RSI drops below 30, put the stock on your watchlist but wait for RSI to rise back above 30 before buying - this confirms the downward momentum is ending. Aggressive approach: Buy when RSI first drops below 30 (catching the falling knife) but use a tight stop loss. Sell when RSI first rises above 70. Advanced tip: Look for divergences - if the stock price makes a new high but RSI makes a lower high, it's a warning signal that the uptrend is weakening."
        },
        "macd": {
            "title": "MACD - Moving Average Convergence Divergence",
            "description": "MACD (pronounced 'mac-dee') is like watching two runners on a track - one sprinter (fast moving average) and one marathon runner (slow moving average). When the sprinter pulls ahead of the marathon runner, it shows the stock is speeding up (bullish). When the sprinter falls behind, it shows the stock is slowing down (bearish). MACD is fantastic for catching momentum shifts and trend changes before they become obvious to everyone else.",
            "what_it_is": "MACD has three components you'll see on the chart: (1) MACD Line (blue line) - the difference between a 12-day fast moving average and a 26-day slow moving average. Think of this as showing the gap between the sprinter and marathon runner. (2) Signal Line (red/orange line) - a 9-day moving average of the MACD line itself. This smooths out the MACD line to give clearer signals. (3) Histogram (green and red bars) - shows the distance between the MACD line and Signal line. Taller bars mean stronger momentum. When bars are above zero and growing, bulls are in control. When bars are below zero and growing, bears are in control.",
            "why_important": "MACD is important because it helps you catch trend reversals early, often before they're obvious on the price chart. It's like having radar that detects changes in the weather before the storm arrives. MACD combines trend-following (which direction) with momentum (how strong) in one indicator. This dual nature makes it incredibly powerful - it tells you not just where the stock is going, but also how strongly it's moving in that direction. Professional traders watch for MACD crossovers as key trigger points for entering or exiting positions. Unlike some indicators that only work in certain market conditions, MACD works well in both trending and ranging markets.",
            "how_to_read": [
                "🟢 MACD Line crosses above Signal Line: Bullish crossover - Buyers are taking control. This is a buy signal, especially if it happens below the zero line (shows momentum changing from negative to positive).",
                "🔴 MACD Line crosses below Signal Line: Bearish crossover - Sellers are taking control. This is a sell signal, especially if it happens above the zero line (shows momentum changing from positive to negative).",
                "📊 Histogram above zero and growing: Bullish momentum is accelerating. The gap between fast and slow averages is widening upward. Strong buying pressure.",
                "📊 Histogram below zero and growing downward: Bearish momentum is accelerating. The gap is widening downward. Strong selling pressure.",
                "🎯 MACD Line crosses above zero line: Very strong bullish signal - The fast average is now above the slow average, confirming uptrend.",
                "⚠️ MACD Line crosses below zero line: Very strong bearish signal - The fast average is now below the slow average, confirming downtrend.",
                "⏸️ Histogram shrinking toward zero: Momentum is weakening, trend may be losing steam. Be prepared for potential reversal.",
                "🔄 Divergence: If price makes new highs but MACD doesn't, it's a bearish divergence (warning of reversal). If price makes new lows but MACD doesn't, it's a bullish divergence (potential bottom)."
            ],
            "signal_contribution": "20%",
            "contribution_explanation": "MACD contributes 20% (second largest) to our trading signal because it's excellent at both confirming trend direction and identifying momentum changes. When MACD shows a bullish crossover (MACD line crossing above signal line), it adds significant weight to a BUY recommendation. When MACD shows a bearish crossover, it adds significant weight to a SELL recommendation. The histogram height tells us how strong the signal is - taller bars mean more confidence in the signal. We also use MACD to filter out false signals from other indicators by checking if momentum supports the move.",
            "beginner_tip": "Focus on the two most important signals as a beginner: (1) Watch for when the MACD line (blue) crosses the Signal line (red). Cross above = potential buy, cross below = potential sell. (2) Pay attention to the histogram bars. When they start shrinking after being very tall, it's a warning that the current trend might be running out of energy. Don't worry about all the complex details at first - just watch for these crossovers and you'll start seeing patterns. Also remember: MACD works best in trending markets and can give false signals in sideways, choppy markets. Always check if the stock is in a trend first.",
            "trading_strategy": "Entry strategy: Buy when MACD line crosses above the signal line AND both lines are rising AND the histogram is growing (all three confirm the bullish signal). For strongest signals, wait for this crossover to happen below the zero line (means you're catching the reversal early). Exit strategy: Sell when MACD line crosses below signal line, or when the histogram starts shrinking significantly even if there's no crossover (early warning of weakening momentum). Advanced technique: Use MACD for confirmation with other indicators - for example, buy when RSI bounces from oversold levels AND MACD shows a bullish crossover. This gives you multiple confirmations and reduces false signals."
        },
        "moving_averages": {
            "title": "Moving Averages (SMA) - Trend Direction Indicators",
            "description": "Moving averages are like using a blender to smooth out a bumpy smoothie - they take all the daily up-and-down price movements and blend them into a smooth line that shows you the overall direction. Imagine trying to see the trend of ocean waves while standing on the beach - individual waves go up and down chaotically, but the tide (the moving average) clearly shows if water is rising or falling. Moving averages filter out the 'noise' of daily price swings to reveal the true underlying trend.",
            "what_it_is": "A Simple Moving Average (SMA) adds up the closing prices for a certain number of days and divides by that number to get the average. We use three timeframes: SMA 20 (past 20 trading days, about 1 month) shows the short-term trend - where the stock has been going recently. SMA 50 (past 50 trading days, about 2.5 months) shows the medium-term trend - the stock's direction over the past quarter. SMA 200 (past 200 trading days, about 10 months) shows the long-term trend - the big picture direction and is watched by institutional investors globally. For example, if IBM's 20-day SMA is $150, it means the average price over the past 20 days was $150.",
            "why_important": "Moving averages are important because they answer the most fundamental trading question: 'Which direction is this stock actually going?' Daily prices bounce around due to news, emotions, and random trading, making it hard to see the real trend. Moving averages cut through this chaos to show you the truth. They're like a compass in the wilderness - when you're lost in confusing price action, moving averages point you in the right direction. Additionally, moving averages act as dynamic support and resistance levels. When a stock is in an uptrend, it often bounces off its moving averages like a trampoline, giving you ideal entry points. Institutional traders and algorithms use moving averages to make billion-dollar decisions, so when millions of traders are watching the same levels, they become self-fulfilling prophecies.",
            "how_to_read": [
                "📈 Price above SMA: Uptrend confirmed - Bulls are in control. The average price over the period is rising. This is bullish territory. Stay long or look for buying opportunities on dips.",
                "📉 Price below SMA: Downtrend confirmed - Bears are in control. The average price is falling. This is bearish territory. Avoid buying or consider selling/shorting.",
                "🚀 Golden Cross (SMA 50 crosses above SMA 200): Extremely bullish signal - Often marks the beginning of major uptrends. Big money starts buying. This is one of the most famous signals in technical analysis.",
                "💀 Death Cross (SMA 50 crosses below SMA 200): Extremely bearish signal - Often marks the beginning of major downtrends. Big money starts selling. Time to protect your capital.",
                "🎯 Bullish stack (Price > SMA20 > SMA50 > SMA200): Perfect alignment - All time frames are trending up. This is as bullish as it gets. Strong buying momentum across all timeframes.",
                "⚠️ Bearish stack (Price < SMA20 < SMA50 < SMA200): Perfect misalignment - All time frames are trending down. This is as bearish as it gets. Strong selling pressure across all timeframes.",
                "🔄 Price bouncing off SMA: Dynamic support/resistance - In uptrends, price often pulls back to SMA then bounces up. In downtrends, price rallies to SMA then gets rejected. These bounces are classic entry/exit points.",
                "📏 Distance between SMAs: Shows trend strength - Wider gaps mean stronger trends. Narrowing gaps mean trend is weakening. When SMAs bunch together, a big move is usually coming."
            ],
            "signal_contribution": "18%",
            "contribution_explanation": "Moving averages contribute 18% to our trading signal because they provide the essential trend context that frames everything else. Think of them as the foundation of a house - other indicators tell you details about the rooms, but moving averages tell you if the foundation is solid. When the price is above rising moving averages, it adds bullish weight to our signal. When price is below falling averages, it adds bearish weight. The relationship between different moving averages (Golden Cross, Death Cross, stacking) provides additional confirmation. We give particular importance to the 50-day and 200-day SMAs because they're watched by institutional investors managing trillions of dollars.",
            "beginner_tip": "Start by focusing on just one rule: Don't fight the trend. If price is above the 50-day SMA, look for buying opportunities. If price is below the 50-day SMA, avoid buying or consider selling. That's it. As you get more comfortable, you can add complexity like watching for Golden Crosses or trading bounces off the 20-day SMA. Think of moving averages like river currents - swimming with the current (trading with the trend) is easy and profitable. Swimming against the current (trading against the trend) is exhausting and usually unsuccessful. The moving averages show you which way the current is flowing.",
            "trading_strategy": "Trend following strategy: Only buy when price is above the 50-day SMA and the 50-day is above the 200-day SMA (both trending up). This keeps you on the right side of the trend. Pullback strategy: When price is above the 20-day SMA (uptrend), wait for price to pull back and touch or slightly dip below the 20-day SMA, then buy when it bounces back above (the moving average acts as support). This lets you buy dips in strong stocks. Crossover strategy: Buy when the 20-day SMA crosses above the 50-day SMA (shows short-term trend is beating medium-term trend). Sell when the 20-day crosses below the 50-day. For long-term investing, watch for the Golden Cross (50 crossing above 200) as a major buy signal and Death Cross (50 crossing below 200) as a major sell signal. Risk management: Use the 200-day SMA as your line in the sand - if a stock you own closes below its 200-day SMA, seriously consider selling to protect capital."
        },
        "volume": {
            "title": "Volume Analysis - Market Participation Indicator",
            "description": "Volume is like counting how many people showed up to vote in an election - it tells you how many traders are putting their money where their mouth is. High volume means lots of people (both buyers and sellers) are actively participating in the price move, making it legitimate and sustainable. Low volume means only a few traders are involved, making the price move weak and likely to reverse. Think of volume as the 'conviction' behind a price move - the more people participating, the more conviction, the more reliable the signal.",
            "what_it_is": "Volume simply measures how many shares changed hands during a specific time period (usually a day). For example, if IBM has a volume of 5 million shares, that means 5 million shares were bought AND sold (every transaction has a buyer and a seller). We compare today's volume to the average volume over the past 50 days to determine if participation is normal, high, or low. A Volume Ratio of 1.5 means today's volume is 50% higher than average - lots of unusual activity. A ratio of 0.5 means volume is half the normal amount - very quiet trading. Volume is counted in actual shares traded, so larger companies naturally have higher absolute volume numbers than smaller companies.",
            "why_important": "Volume is crucial because it separates real moves from fake ones. Imagine this: A stock moves up $5 on low volume (only 100,000 shares) versus moving up $5 on high volume (10 million shares). Which move is more trustworthy? The high volume move, because millions of traders agreed the stock should be worth more. The low volume move might just be a few large orders pushing the price around temporarily. Volume confirms or denies price action. Professional traders have a saying: 'Volume precedes price' - meaning big volume often appears before major price moves. Institutions (big money) can't hide their footprints - when they're buying or selling millions of shares, volume spikes. By watching volume, you can see what the smart money is doing before the price fully reflects their actions.",
            "how_to_read": [
                "🟢 High volume + Price rising: Strong bullish confirmation - Many buyers are aggressively buying. There's real demand. This upward move is legitimate and likely to continue. Smart money is accumulating.",
                "🔴 High volume + Price falling: Strong bearish confirmation - Many sellers are aggressively selling. There's real supply. This downward move is legitimate and likely to continue. Smart money is distributing.",
                "⚠️ Low volume + Price rising: Weak bullish signal - Only a few traders are buying. There's no real excitement or demand. This rise is probably temporary and will reverse. Don't chase it.",
                "⚠️ Low volume + Price falling: Weak bearish signal - Only a few traders are selling. There's no panic or real supply. This decline is probably temporary. Might be a buying opportunity if fundamentals are strong.",
                "📊 Volume Ratio > 1.5: Above average participation - Something is happening. News, earnings, or institutional activity. Pay attention. Big moves often follow high volume days.",
                "📊 Volume Ratio < 0.7: Below average participation - Quiet day, not much interest. Price moves on low volume days are less meaningful. Wait for volume to return before making decisions.",
                "💥 Volume spike on breakout: Valid breakout - When price breaks resistance with huge volume, it confirms the breakout is real. This is one of the strongest buy signals.",
                "🚫 Low volume on breakout: False breakout likely - When price breaks resistance on low volume, it's probably a fake-out. Price will likely fall back below resistance soon."
            ],
            "signal_contribution": "15%",
            "contribution_explanation": "Volume contributes 15% to our trading signal because it acts as a 'truth detector' for all other signals. Even if RSI, MACD, and moving averages all look bullish, if volume is low, we reduce confidence in the buy signal. Conversely, high volume during bullish setups increases our confidence significantly. We specifically look for: (1) Confirmation - high volume should accompany strong price moves in the direction of the trend. (2) Exhaustion - extremely high volume after extended moves often signals reversals. (3) Breakouts - volume must spike during breakouts for them to be valid. Volume essentially validates or invalidates what price is telling us.",
            "beginner_tip": "Here's the simplest way to use volume: Look at the volume bars at the bottom of your chart. Are they taller than usual (high volume) or shorter than usual (low volume)? Now look at the price. Is it going up or down? If price is going up on tall volume bars = good, trust the move. If price is going up on short volume bars = suspicious, don't trust it. If price is going down on tall volume bars = bad, real selling pressure. If price is going down on short volume bars = probably temporary, not scary. That's it! As you get more experienced, you'll start noticing patterns like volume drying up before big moves (calm before the storm) or volume exploding at tops and bottoms (climax volumes).",
            "trading_strategy": "Breakout strategy: Only buy breakouts (price moving above resistance) when volume is at least 1.5x average volume. High volume breakouts rarely fail. Low volume breakouts almost always fail. Trend confirmation: In uptrends, look for high volume on up days and low volume on down days (shows buyers are strong, sellers are weak). Reverse for downtrends. Divergence strategy: If price makes new highs but volume is declining, it's a bearish divergence (uptrend losing steam). Consider taking profits. If price makes new lows but volume is declining, it's a bullish divergence (downtrend losing steam). Consider buying. Entry timing: Look for high volume selling climaxes (huge red volume bar with big price drop) in quality stocks - these often mark short-term bottoms and create buying opportunities. Exit timing: Watch for high volume exhaustion moves (huge green volume bar after extended rally) - these often mark short-term tops."
        },
        "bollinger": {
            "title": "Bollinger Bands - Volatility and Mean Reversion Indicator",
            "description": "Bollinger Bands are like drawing flexible guardrails around price movement. Imagine driving on a highway where the lanes automatically widen when traffic gets crazy (high volatility) and narrow when traffic is calm (low volatility). These bands show you the 'normal' range where price should be trading, and alert you when price is stretching to extremes. When price touches the outer bands, it's like a car touching the lane markers - it usually corrects back toward the center. Bollinger Bands adapt to market conditions automatically, making them incredibly versatile.",
            "what_it_is": "Bollinger Bands consist of three components: (1) Middle Band: This is simply the 20-day Simple Moving Average (SMA 20) - the average price over the past 20 days. Think of this as the 'normal' or 'fair' price. (2) Upper Band: Set 2 standard deviations above the middle band. This represents the 'expensive' zone - where price is stretched high. (3) Lower Band: Set 2 standard deviations below the middle band. This represents the 'cheap' zone - where price is stretched low. The 2 standard deviations means that statistically, price should stay within the bands about 95% of the time. The %B indicator tells you where price is relative to the bands: %B of 1.0 means price is at the upper band, %B of 0.0 means price is at the lower band, %B of 0.5 means price is at the middle band (perfectly normal).",
            "why_important": "Bollinger Bands are important for three key reasons: (1) Mean Reversion - They show when price has moved too far from average and is likely to snap back (like a rubber band). Most of the time, when price hits extreme bands, it bounces back. (2) Volatility Measurement - The width between bands tells you how volatile the stock is. Wide bands = wild price swings. Narrow bands = calm, predictable movement. (3) Breakout Prediction - When bands squeeze together tightly (very narrow), it means volatility is extremely low, which almost always precedes a big breakout move. It's like compressed energy waiting to explode. The bands automatically adjust to current market conditions - expanding during volatile periods and contracting during calm periods. This self-adjusting nature makes them work in all market environments.",
            "how_to_read": [
                "🔴 Price at Upper Band: Overbought signal - Price is at the 'expensive' extreme, 2 standard deviations above normal. Often leads to pullbacks. In strong uptrends, price can 'walk the upper band' for extended periods, but eventually pulls back.",
                "🟢 Price at Lower Band: Oversold signal - Price is at the 'cheap' extreme, 2 standard deviations below normal. Often leads to bounces. Good buying opportunity in quality stocks.",
                "⚪ Price at Middle Band (20 SMA): Normal price level - Price is trading at fair value. Neither overbought nor oversold. Neutral zone.",
                "📏 Wide Bands (expanding): High volatility - The stock is making big moves. Expect continued large price swings. Bands expand after breakouts. This is when trends accelerate.",
                "🔒 Narrow Bands (contracting): Low volatility - The stock is calm, trading in a tight range. This is the 'squeeze' - volatility is compressed like a coiled spring. A big move is coming soon but we don't know which direction yet.",
                "💥 Bollinger Squeeze: Bands at narrowest point in months - This is one of the most powerful setups. Extremely low volatility is about to explode into a big trending move. Wait for the breakout direction, then trade with it.",
                "📊 %B Above 0.8: Near upper band territory - Price is in the overbought zone. %B = 1.0 means exactly at upper band. Consider taking profits or waiting for better entry.",
                "📊 %B Below 0.2: Near lower band territory - Price is in the oversold zone. %B = 0.0 means exactly at lower band. Consider buying opportunities.",
                "🔄 Band Walk: Price hugging one band - In strong trends, price can walk along the upper or lower band for weeks. This shows exceptional strength (upper band walk) or weakness (lower band walk)."
            ],
            "signal_contribution": "12%",
            "contribution_explanation": "Bollinger Bands contribute 12% to our trading signal because they provide crucial context about whether price is at normal, expensive, or cheap levels relative to recent history. When price is near the upper band (%B above 0.8), we reduce our buy signal strength and increase sell signal strength - the stock is stretched high. When price is near the lower band (%B below 0.2), we increase our buy signal strength - the stock is stretched low and likely to bounce, especially in quality stocks. We also use band width to assess volatility and risk. Narrow bands (squeezes) alert us that a big move is imminent, increasing our readiness to act. Wide bands during trends confirm the strength of the move.",
            "beginner_tip": "Start with this simple concept: Bollinger Bands create a channel, and price tends to bounce between the edges of that channel like a pinball. When price hits the upper band, expect it to bounce down toward the middle. When price hits the lower band, expect it to bounce up toward the middle. This works most reliably in sideways, range-bound markets. One warning: In strong trends, the bands can give false signals - price can walk along the upper band in uptrends or lower band in downtrends for extended periods without bouncing. Always check the overall trend direction using moving averages before blindly trading band touches. Also watch for the 'squeeze' - when the bands get very narrow, a big move is coming. Wait for price to break out of the narrow bands, then trade in that direction.",
            "trading_strategy": "Mean reversion strategy (for range-bound markets): Buy when price touches or breaks below the lower band AND RSI is below 30 (double confirmation of oversold). Place a stop loss below the recent swing low. Take profit when price reaches the middle band or upper band. Reverse for sells. Trend following with bands (for trending markets): In uptrends (price above 50-day SMA), use lower band touches as buying opportunities - the band acts as dynamic support. Don't fade the upper band in strong uptrends. In downtrends, use upper band touches as shorting opportunities. Squeeze breakout strategy: Identify when bands are at their narrowest (Bollinger Squeeze). Wait for price to break out of the bands with volume. Buy if it breaks above the upper band with high volume. Sell/short if it breaks below the lower band with high volume. The breakout direction often leads to major moves. Risk management: If you buy at the lower band and price continues to fall through it, exit immediately. When price breaks outside the bands, it's showing exceptional strength or weakness, and the normal bouncing behavior is suspended."
        },
        "support_resistance": {
            "title": "Support & Resistance - Price Level Psychology",
            "description": "Support and resistance are like invisible force fields at specific price levels where the collective memory and psychology of millions of traders creates predictable behavior. Support is like a trampoline - when price falls to this level, buyers jump in and bounce it back up. Resistance is like a ceiling - when price rises to this level, sellers push it back down. These levels exist because human psychology is predictable. Traders remember where they bought or sold before, where they made or lost money, and these memories create patterns that repeat. Understanding these levels is like having a map that shows where the important battles between buyers and sellers will take place.",
            "what_it_is": "Support is a price level where a stock has repeatedly stopped falling and bounced higher. It's where demand (buyers) is strong enough to overcome supply (sellers). Think of it as a floor that catches falling prices. Resistance is a price level where a stock has repeatedly stopped rising and fallen back. It's where supply (sellers) is strong enough to overcome demand (buyers). Think of it as a ceiling that blocks rising prices. These levels are identified by looking at historical price charts and finding where price has reversed direction multiple times. The more times a level has been tested (touched) without breaking, the stronger it becomes. For example, if IBM bounced off $145 three times in the past six months, $145 is a strong support level. If IBM was rejected at $160 four times, $160 is a strong resistance level. Round numbers (like $50, $100, $150) often act as psychological support/resistance because humans naturally think in round numbers.",
            "why_important": "Support and resistance are crucial because they tell you where the next big battle between buyers and sellers will happen, allowing you to position yourself advantageously. They provide specific price targets for entries and exits, making your trading plan concrete rather than abstract. They represent collective market memory - thousands of traders who bought at $150 will defend that level to avoid losses. Traders who missed buying at $150 will buy when it returns. Traders who sold at $150 and regret it will buy when it comes back. This creates self-fulfilling prophecies. Support and resistance also help with risk management - you know exactly where to place stop losses (just below support for longs, just above resistance for shorts). When these levels break, they often lead to explosive moves because all the orders that were defending the level are now exhausted, and price can move freely until the next major level. Professional traders plan their entire strategy around these levels.",
            "how_to_read": [
                "🟢 Price approaching Support from above: High probability bounce zone - Buyers typically step in here. Good place to look for long entries. The closer price gets without breaking, the more buyers accumulate.",
                "🔴 Price approaching Resistance from below: High probability rejection zone - Sellers typically step in here. Good place to take profits on longs or look for short entries. The closer price gets without breaking, the more sellers distribute.",
                "💔 Support broken (price closes below): Bearish signal - Buyers gave up. Level failed. Often leads to accelerated selling as stop losses trigger. Old support often becomes new resistance (role reversal). Very bearish.",
                "🚀 Resistance broken (price closes above): Bullish signal - Sellers gave up. Level failed. Often leads to accelerated buying as traders chase the breakout. Old resistance often becomes new support (role reversal). Very bullish.",
                "💪 Multiple touches without breaking: Level strengthening - Each time price tests a level and bounces, it becomes stronger. The level is validated. More traders pay attention to it. Like testing a rope repeatedly - each test that holds makes you trust it more.",
                "📍 Round number levels (100, 150, 200): Strong psychological barriers - Humans think in round numbers. Option strikes are at round numbers. Institutions place orders at round numbers. These levels naturally attract activity.",
                "🔄 Role Reversal: Broken support becomes resistance, broken resistance becomes support - This is one of the most reliable patterns. Once a support level breaks, all the traders who bought there now have losses. When price returns to that level, they sell to break even, creating new resistance.",
                "📊 Support/Resistance zones vs. exact prices: Levels are zones, not exact numbers - Don't expect price to bounce at exactly $145.00. Support might be $144.50-$145.50. Use zones, not precise points. Gives you flexibility.",
                "⚡ False breakouts (fakeouts): Brief breaks that quickly reverse - Price may spike above resistance or below support to trigger stop losses, then reverse. This is why we wait for closing prices, not intraday spikes. Professionals hunt for your stop losses."
            ],
            "signal_contribution": "10%",
            "contribution_explanation": "Support and resistance contribute 10% to our trading signal by identifying the most important price levels for decision-making. When price is near strong support, we increase the buy signal weight - the level is likely to hold and bounce. When price is near strong resistance, we decrease the buy signal weight and increase the sell signal weight - the level is likely to cause a rejection. We also consider the strength of the level (how many times it's been tested) and the volume when testing the level. High volume tests that hold are more significant. Additionally, we watch for level breaks - when support or resistance breaks with high volume, it often signals the start of major moves, and we adjust our signals accordingly. The cleaner and more obvious the support/resistance level, the more weight we give it in our analysis.",
            "beginner_tip": "Imagine support and resistance like floors and ceilings in a multi-story building. Price bounces between these levels like a ball in a room. The ball will bounce between the floor and ceiling repeatedly until something breaks. To find these levels on a chart, zoom out and look for areas where price has reversed direction multiple times - these obvious turning points are your support and resistance zones. Draw horizontal lines at these levels. When price approaches these lines in the future, pay close attention - something interesting is about to happen (bounce or break). Start by only trading the obvious, strong levels that anyone can see. Don't try to trade every tiny support or resistance - focus on the major ones where price has reversed 3 or more times. One key trick: Use previous resistance as new support after breakouts. This 'role reversal' is incredibly reliable and one of the safest trade setups.",
            "trading_strategy": "Bounce trading strategy: Buy when price approaches strong support (within 1-2% of the level) with a stop loss just below support (2-3% below). Target the next resistance level or middle of the range. This gives excellent risk/reward. Reverse for shorting at resistance. Breakout trading strategy: Wait for price to break and close above resistance on high volume (1.5x average). Buy on the first pullback to the old resistance (now new support). This minimizes risk - if the breakout is real, old resistance will hold as new support. If it fails, you're stopped out quickly. Sell strategy: Take profits near resistance levels. As price approaches resistance, tighten stop losses. Don't hope for resistance to break - take your profits and wait to see if it breaks. You can always re-enter after a confirmed break. Range trading strategy: If a stock is stuck between clear support and resistance, buy near support and sell near resistance repeatedly until the range breaks. This is low-risk, predictable trading. False breakout protection: Don't trade breakouts until the candle closes beyond the level. Intraday spikes don't count. Wait for daily close confirmation. Also, wait for the first pullback after the breakout - this gives better entry price and confirmation that the breakout is real. Zone trading: Support and resistance are zones, not exact prices. Enter positions anywhere in the support zone (a few dollars wide) rather than waiting for an exact price that might never hit."
        }
    }
    
    # Topic aliases for backward compatibility and different naming conventions
    topic_aliases = {
        "sma": "moving_averages",
        "support": "support_resistance"
    }
    
    # Check if topic exists directly or through alias
    actual_topic = topic_aliases.get(topic, topic)
    
    if actual_topic in educational_content:
        return educational_content[actual_topic]
    else:
        raise HTTPException(status_code=404, detail="Educational content not found")


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    account_type: str
    profile_data: Dict[str, Any]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str

@app.post("/api/auth/signup", response_model=TokenResponse)
async def signup(request: SignupRequest, req: Request, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Validate email
        if not auth.validate_email(request.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Check if user already exists
        existing_user = auth.get_user_by_email(db, request.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Validate password
        is_valid, message = auth.validate_password(request.password)
        if not is_valid:
            raise HTTPException(status_code=400, detail=message)
        
        # Validate account type (only stocks supported)
        if request.account_type != "stocks":
            raise HTTPException(status_code=400, detail="Invalid account type. Only 'stocks' accounts are supported.")
        
        # Check for public company insider
        if request.profile_data.get("is_public_company_insider"):
            raise HTTPException(
                status_code=403, 
                detail="Public company insiders cannot open an account at this time"
            )
        
        # Create user
        user = auth.create_user(db, request.email, request.password, request.account_type)
        
        # Create user profile
        auth.create_user_profile(db, user.id, request.profile_data)
        
        # Create session
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent")
        session = auth.create_session(db, user.id, ip_address, user_agent)
        
        # Create access token
        access_token = auth.create_access_token(data={"sub": str(user.id), "email": user.email})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Signup error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during registration")


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest, req: Request, db: Session = Depends(get_db)):
    """Login user"""
    try:
        # Authenticate user
        user = auth.authenticate_user(db, request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")
        
        # Create session
        ip_address = req.client.host if req.client else None
        user_agent = req.headers.get("user-agent")
        session = auth.create_session(db, user.id, ip_address, user_agent)
        
        # Create access token
        access_token = auth.create_access_token(data={"sub": str(user.id), "email": user.email})
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during login")


@app.post("/api/auth/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Logout user"""
    try:
        token = credentials.credentials
        payload = auth.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Invalidate session
        # Note: We're using JWT tokens, so we can't truly invalidate them
        # In production, you'd want to use a token blacklist
        
        return {"message": "Logged out successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during logout")


@app.get("/api/auth/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get current user information"""
    try:
        token = credentials.credentials
        payload = auth.verify_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_id = int(payload.get("sub"))
        user = auth.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        profile = auth.get_user_profile(db, user_id)
        
        return {
            "user_id": user.id,
            "email": user.email,
            "account_type": user.account_type,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat(),
            "profile": {
                "first_name": profile.first_name if profile else None,
                "last_name": profile.last_name if profile else None,
                "preferred_name": profile.preferred_name if profile else None
            } if profile else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Get user error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred")


@app.get("/api/auth/check-email/{email}")
async def check_email(email: str, db: Session = Depends(get_db)):
    """Check if email is already registered"""
    user = auth.get_user_by_email(db, email)
    return {"available": user is None}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
