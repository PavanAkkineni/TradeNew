"""
Market Data Aggregation Engine
This component fetches raw market data from various APIs without interpretation.
Acts as a pure "fact-finding" layer.
"""
import os
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import time
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory cache for market data
_market_data_cache = {
    'data': None,
    'timestamp': None,
    'ttl_minutes': 60  # Cache for 60 minutes
}


class MarketDataAggregator:
    """
    Aggregates market data from multiple sources:
    - Economic indicators (FRED API)
    - Market performance (Alpha Vantage / Finnhub)
    - Market sentiment (NewsAPI)
    """
    
    def __init__(self):
        """Initialize with API keys from environment variables"""
        self.fred_api_key = os.getenv('FRED_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY', '')
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        
        # Base URLs
        self.fred_base_url = "https://api.stlouisfed.org/fred/series/observations"
        self.alpha_vantage_base_url = "https://www.alphavantage.co/query"
        self.finnhub_base_url = "https://finnhub.io/api/v1"
        self.news_api_base_url = "https://newsapi.org/v2"
        
    def fetch_economic_indicators(self) -> Dict[str, Any]:
        """
        Fetch economic indicators from FRED API
        Returns raw data without interpretation
        """
        logger.info("Fetching economic indicators from FRED API...")
        
        indicators = {}
        
        # Define FRED series IDs for each indicator
        fred_series = {
            'inflation_rate': 'CPIAUCSL',  # Consumer Price Index
            'federal_funds_rate': 'DFF',    # Federal Funds Effective Rate
            'gdp_growth_rate': 'A191RL1Q225SBEA',  # Real GDP Growth
            'unemployment_rate': 'UNRATE'   # Unemployment Rate
        }
        
        for indicator_name, series_id in fred_series.items():
            try:
                data = self._fetch_fred_series(series_id)
                indicators[indicator_name] = data
                logger.info(f"✅ Fetched {indicator_name}: {data.get('value', 'N/A')}")
            except Exception as e:
                logger.error(f"❌ Error fetching {indicator_name}: {str(e)}")
                indicators[indicator_name] = {
                    'value': None,
                    'date': None,
                    'error': str(e),
                    'series_id': series_id
                }
        
        return indicators
    
    def _fetch_fred_series(self, series_id: str, limit: int = 1) -> Dict[str, Any]:
        """
        Fetch latest observation from a FRED series
        """
        if not self.fred_api_key:
            return {
                'value': None,
                'date': None,
                'error': 'FRED API key not configured',
                'series_id': series_id
            }
        
        params = {
            'series_id': series_id,
            'api_key': self.fred_api_key,
            'file_type': 'json',
            'sort_order': 'desc',
            'limit': limit
        }
        
        response = requests.get(self.fred_base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        observations = data.get('observations', [])
        
        if observations:
            latest = observations[0]
            return {
                'value': float(latest['value']) if latest['value'] != '.' else None,
                'date': latest['date'],
                'series_id': series_id,
                'units': data.get('units', 'N/A')
            }
        else:
            return {
                'value': None,
                'date': None,
                'series_id': series_id,
                'error': 'No observations found'
            }
    
    def fetch_market_performance(self) -> Dict[str, Any]:
        """
        Fetch market performance metrics
        - S&P 500 (price, 50-day MA, 200-day MA)
        - VIX Index
        - US 10-Year Treasury Yield
        - Gold spot price
        - VNQ ETF (Real Estate proxy)
        """
        logger.info("Fetching market performance data...")
        
        market_data = {}
        
        # Define symbols to fetch (using ETFs that Alpha Vantage supports)
        symbols = {
            'sp500': 'SPY',        # S&P 500 ETF (tracks ^GSPC)
            'vix': 'VXX',          # VIX ETF (tracks volatility)
            'treasury_10y': 'TLT', # 20+ Year Treasury ETF
            'gold': 'GLD',         # Gold ETF (tracks gold prices)
            'vnq': 'VNQ'           # Vanguard Real Estate ETF
        }
        
        for key, symbol in symbols.items():
            try:
                data = self._fetch_symbol_data(symbol)
                market_data[key] = data
                logger.info(f"✅ Fetched {key}: ${data.get('current_price', 'N/A')}")
                
                # Add small delay between API calls
                # Finnhub: 60 calls/minute (1 per second is safe)
                # Using 0.2 seconds for faster loading
                time.sleep(0.2)
                
            except Exception as e:
                logger.error(f"❌ Error fetching {key}: {str(e)}")
                market_data[key] = {
                    'symbol': symbol,
                    'error': str(e),
                    'current_price': None
                }
                # Small delay even on error
                time.sleep(0.2)
        
        return market_data
    
    def _fetch_symbol_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch price and moving averages for a symbol
        Uses Finnhub or Alpha Vantage API (Finnhub preferred for better rate limits)
        """
        # Try Finnhub first (60 calls/minute vs Alpha Vantage's 25/day)
        if self.finnhub_key:
            try:
                return self._fetch_finnhub_data(symbol)
            except Exception as e:
                logger.warning(f"Finnhub failed for {symbol}, trying Alpha Vantage: {e}")
                if self.alpha_vantage_key:
                    return self._fetch_alpha_vantage_data(symbol)
                else:
                    raise
        elif self.alpha_vantage_key:
            return self._fetch_alpha_vantage_data(symbol)
        else:
            return {
                'symbol': symbol,
                'current_price': None,
                'ma_50': None,
                'ma_200': None,
                'error': 'No API key configured for market data'
            }
    
    def _fetch_alpha_vantage_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch data from Alpha Vantage API
        """
        # Get daily time series
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'apikey': self.alpha_vantage_key,
            'outputsize': 'compact'  # Last 100 days
        }
        
        response = requests.get(self.alpha_vantage_base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'Time Series (Daily)' not in data:
            return {
                'symbol': symbol,
                'current_price': None,
                'error': data.get('Note', 'API limit reached or invalid symbol')
            }
        
        time_series = data['Time Series (Daily)']
        dates = sorted(time_series.keys(), reverse=True)
        
        if not dates:
            return {
                'symbol': symbol,
                'current_price': None,
                'error': 'No data available'
            }
        
        # Current price (most recent close)
        latest_date = dates[0]
        current_price = float(time_series[latest_date]['4. close'])
        
        # Calculate moving averages
        ma_50 = self._calculate_ma(time_series, dates, 50)
        ma_200 = self._calculate_ma(time_series, dates, 200)
        
        # Get 52-week high (for gold)
        week_52_high = self._get_52_week_high(time_series, dates)
        
        return {
            'symbol': symbol,
            'current_price': current_price,
            'ma_50': ma_50,
            'ma_200': ma_200,
            'week_52_high': week_52_high,
            'last_updated': latest_date,
            'api_source': 'Alpha Vantage'
        }
    
    def _fetch_finnhub_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch data from Finnhub API as fallback
        """
        headers = {'X-Finnhub-Token': self.finnhub_key}
        
        # Get current quote
        quote_url = f"{self.finnhub_base_url}/quote"
        params = {'symbol': symbol}
        
        response = requests.get(quote_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        
        quote_data = response.json()
        
        return {
            'symbol': symbol,
            'current_price': quote_data.get('c'),  # Current price
            'high': quote_data.get('h'),           # High price of the day
            'low': quote_data.get('l'),            # Low price of the day
            'previous_close': quote_data.get('pc'), # Previous close
            'api_source': 'Finnhub'
        }
    
    def _calculate_ma(self, time_series: Dict, dates: List[str], period: int) -> Optional[float]:
        """
        Calculate moving average for a given period
        """
        if len(dates) < period:
            return None
        
        prices = [float(time_series[date]['4. close']) for date in dates[:period]]
        return sum(prices) / len(prices)
    
    def _get_52_week_high(self, time_series: Dict, dates: List[str]) -> Optional[float]:
        """
        Get 52-week high price
        """
        # 52 weeks ≈ 260 trading days
        period = min(260, len(dates))
        if period < 50:  # Need reasonable amount of data
            return None
        
        highs = [float(time_series[date]['2. high']) for date in dates[:period]]
        return max(highs) if highs else None
    
    def fetch_market_sentiment(self, query: str = "stock market economy", 
                               page_size: int = 10) -> Dict[str, Any]:
        """
        Fetch recent news headlines for market sentiment
        Returns raw headlines without analysis
        """
        logger.info(f"Fetching market sentiment headlines for: '{query}'...")
        
        if not self.news_api_key:
            logger.warning("NewsAPI key not configured")
            return {
                'query': query,
                'headlines': [],
                'error': 'NewsAPI key not configured',
                'total_results': 0
            }
        
        try:
            # Calculate date range (last 7 days)
            to_date = datetime.now()
            from_date = to_date - timedelta(days=7)
            
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': page_size,
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d')
            }
            
            url = f"{self.news_api_base_url}/everything"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'ok':
                return {
                    'query': query,
                    'headlines': [],
                    'error': data.get('message', 'Unknown error'),
                    'total_results': 0
                }
            
            # Extract just the headlines and metadata
            articles = data.get('articles', [])
            headlines = []
            
            for article in articles[:page_size]:
                headlines.append({
                    'title': article.get('title'),
                    'source': article.get('source', {}).get('name'),
                    'published_at': article.get('publishedAt'),
                    'url': article.get('url'),
                    'description': article.get('description')
                })
            
            logger.info(f"✅ Fetched {len(headlines)} headlines")
            
            return {
                'query': query,
                'headlines': headlines,
                'total_results': data.get('totalResults', 0),
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching news: {str(e)}")
            return {
                'query': query,
                'headlines': [],
                'error': str(e),
                'total_results': 0
            }
    
    def aggregate_all_data(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Aggregate all market data into a single JSON object
        This is the main method to call for complete market data
        
        Args:
            use_cache: If True, return cached data if available and not expired
        """
        # Check cache first
        if use_cache and _market_data_cache['data'] is not None:
            cache_time = _market_data_cache['timestamp']
            if cache_time:
                age_minutes = (datetime.now() - cache_time).total_seconds() / 60
                if age_minutes < _market_data_cache['ttl_minutes']:
                    logger.info(f"📦 Returning cached market data (age: {age_minutes:.1f} minutes)")
                    return _market_data_cache['data']
                else:
                    logger.info(f"⏰ Cache expired (age: {age_minutes:.1f} minutes), fetching fresh data")
        
        logger.info("=" * 60)
        logger.info("Starting Market Data Aggregation...")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Fetch all data components
        economic_indicators = self.fetch_economic_indicators()
        market_performance = self.fetch_market_performance()
        market_sentiment = self.fetch_market_sentiment()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Package everything into clean JSON structure
        market_data = {
            'timestamp': datetime.now().isoformat(),
            'data_sources': {
                'economic_indicators': 'FRED API',
                'market_performance': 'Alpha Vantage / Finnhub',
                'market_sentiment': 'NewsAPI'
            },
            'economic_indicators': economic_indicators,
            'market_performance': market_performance,
            'market_sentiment': market_sentiment,
            'metadata': {
                'aggregation_duration_seconds': duration,
                'status': 'success',
                'api_keys_configured': {
                    'fred': bool(self.fred_api_key),
                    'alpha_vantage': bool(self.alpha_vantage_key),
                    'finnhub': bool(self.finnhub_key),
                    'news_api': bool(self.news_api_key)
                }
            }
        }
        
        logger.info("=" * 60)
        logger.info(f"✅ Market Data Aggregation Complete! ({duration:.2f}s)")
        logger.info("=" * 60)
        
        # Cache the data
        _market_data_cache['data'] = market_data
        _market_data_cache['timestamp'] = datetime.now()
        logger.info("📦 Market data cached for future requests")
        
        return market_data


# Standalone test function
if __name__ == "__main__":
    """Test the market data aggregator"""
    aggregator = MarketDataAggregator()
    data = aggregator.aggregate_all_data()
    
    import json
    print(json.dumps(data, indent=2))

