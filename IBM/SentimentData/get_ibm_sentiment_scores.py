import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

# Get EODHD API key from environment variable
EODHD_API_KEY = os.getenv('EODHD_API_KEY')

if not EODHD_API_KEY:
    raise ValueError("EODHD API key not found. Please set EODHD_API_KEY in your .env file")

BASE_URL = 'https://eodhd.com/api/sentiments'
SYMBOL = 'IBM.US'  # EODHD format

def fetch_sentiment_scores(from_date=None, to_date=None):
    """
    Fetch historical sentiment scores for IBM from EODHD API.
    
    Sentiment scores are aggregated daily from news and social media.
    Score range: -1 (very negative) to +1 (very positive)
    
    According to documentation, we need 90 days minimum for pattern analysis.
    
    Parameters:
    -----------
    from_date : str, optional
        Start date in YYYY-MM-DD format. Defaults to 90 days ago.
    to_date : str, optional
        End date in YYYY-MM-DD format. Defaults to today.
    
    Returns:
    --------
    dict : Sentiment data by ticker
    """
    
    # Default to 90 days (recommended for sentiment pattern analysis)
    if not from_date:
        from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        's': SYMBOL,
        'from': from_date,
        'to': to_date,
        'api_token': EODHD_API_KEY,
        'fmt': 'json'
    }
    
    print(f"\nFetching sentiment scores for {SYMBOL}...")
    print(f"Date range: {from_date} to {to_date}")
    print("-" * 60)
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, dict) and SYMBOL in data:
            scores = data[SYMBOL]
            print(f"✅ Retrieved {len(scores)} daily sentiment scores")
            return data
        else:
            print(f"⚠️ Unexpected response format: {type(data)}")
            return {}
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return {}


def analyze_sentiment_scores(data):
    """Analyze sentiment score data and display summary."""
    
    if not data or SYMBOL not in data:
        print("No sentiment data to analyze")
        return
    
    scores = data[SYMBOL]
    
    if not scores:
        print("No sentiment scores found")
        return
    
    print(f"\n📊 SENTIMENT SCORE ANALYSIS:")
    print(f"Total days: {len(scores)}")
    
    # Extract metrics
    dates = [s['date'] for s in scores]
    normalized_scores = [s['normalized'] for s in scores]
    counts = [s['count'] for s in scores]
    
    print(f"Date range: {dates[-1]} to {dates[0]}")
    
    # Statistical summary
    avg_score = sum(normalized_scores) / len(normalized_scores)
    max_score = max(normalized_scores)
    min_score = min(normalized_scores)
    avg_count = sum(counts) / len(counts)
    
    print(f"\n📈 STATISTICS:")
    print(f"  Average Score: {avg_score:.4f}")
    print(f"  Max Score: {max_score:.4f} (on {scores[normalized_scores.index(max_score)]['date']})")
    print(f"  Min Score: {min_score:.4f} (on {scores[normalized_scores.index(min_score)]['date']})")
    print(f"  Average Articles/Day: {avg_count:.1f}")
    
    # Categorize overall sentiment
    if avg_score > 0.3:
        sentiment_label = "🟢 STRONGLY BULLISH"
    elif avg_score > 0.1:
        sentiment_label = "🟡 BULLISH"
    elif avg_score > -0.1:
        sentiment_label = "⚪ NEUTRAL"
    elif avg_score > -0.3:
        sentiment_label = "🟠 BEARISH"
    else:
        sentiment_label = "🔴 STRONGLY BEARISH"
    
    print(f"\n  Overall Sentiment (90d): {sentiment_label}")
    
    # Trend analysis
    recent_scores = normalized_scores[:10]  # Last 10 days
    older_scores = normalized_scores[-10:]  # First 10 days
    
    recent_avg = sum(recent_scores) / len(recent_scores)
    older_avg = sum(older_scores) / len(older_scores)
    
    print(f"\n📊 TREND:")
    print(f"  Last 10 days avg: {recent_avg:.4f}")
    print(f"  First 10 days avg: {older_avg:.4f}")
    
    if recent_avg > older_avg + 0.1:
        trend = "📈 IMPROVING (sentiment getting more positive)"
    elif recent_avg < older_avg - 0.1:
        trend = "📉 DETERIORATING (sentiment getting more negative)"
    else:
        trend = "➡️ STABLE (no significant change)"
    
    print(f"  Trend: {trend}")
    
    # Identify significant days
    print(f"\n🔍 SIGNIFICANT DAYS:")
    
    # Most positive days
    sorted_by_score = sorted(scores, key=lambda x: x['normalized'], reverse=True)
    print(f"\n  Top 3 Most Positive Days:")
    for i, day in enumerate(sorted_by_score[:3]):
        print(f"    {i+1}. {day['date']}: {day['normalized']:.4f} ({day['count']} articles)")
    
    # Most negative days
    print(f"\n  Top 3 Most Negative Days:")
    for i, day in enumerate(sorted_by_score[-3:]):
        print(f"    {i+1}. {day['date']}: {day['normalized']:.4f} ({day['count']} articles)")
    
    # Days with most articles (high attention)
    sorted_by_count = sorted(scores, key=lambda x: x['count'], reverse=True)
    print(f"\n  Days with Most News Coverage:")
    for i, day in enumerate(sorted_by_count[:3]):
        print(f"    {i+1}. {day['date']}: {day['count']} articles (score: {day['normalized']:.4f})")


def save_to_file(data, filename=None):
    """Save sentiment scores to JSON file."""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"sentiment_scores_{timestamp}.json"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    file_size = os.path.getsize(filepath)
    print(f"\n💾 Data saved to: {filename}")
    print(f"📦 File size: {file_size / 1024:.1f} KB")
    
    return filepath


def main():
    """
    Fetch 90 days of historical sentiment scores for IBM.
    
    Purpose:
    - Track daily sentiment trends
    - Identify sentiment spikes (positive or negative)
    - Correlate with news events
    - Generate sentiment-based signals
    """
    
    print("=" * 60)
    print("FETCHING HISTORICAL SENTIMENT SCORES FOR IBM")
    print("=" * 60)
    print("Source: EODHD Sentiment Data API")
    print("Target: 90 days of daily sentiment scores")
    print("Score Range: -1 (very negative) to +1 (very positive)")
    print("=" * 60)
    
    # Calculate date range (90 days)
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Fetch sentiment scores
    data = fetch_sentiment_scores(from_date, to_date)
    
    if data and SYMBOL in data:
        # Analyze the data
        analyze_sentiment_scores(data)
        
        # Save to file
        save_to_file(data)
        
        print("\n" + "=" * 60)
        print("📊 SENTIMENT SCORES FETCH COMPLETE")
        print("=" * 60)
        
        print("\n🎯 USE CASES:")
        print("  • Sentiment trend identification (bullish/bearish)")
        print("  • Spike detection (unusual positive/negative days)")
        print("  • Correlation with price movements")
        print("  • Lead/lag analysis (sentiment before price)")
        print("  • Signal generation (sentiment-based trades)")
        
        print("\n💡 RELATIONSHIP WITH FINANCIAL NEWS:")
        print("  • Sentiment Score = Aggregation of news articles")
        print("  • High score → Check news for positive catalysts")
        print("  • Low score → Check news for negative events")
        print("  • Score spike → Major announcement or event")
        print("  • High article count → Increased attention/volatility")
        
        print("\n📊 PATTERN RECOGNITION:")
        print("  • Identify which sentiment levels trigger price moves")
        print("  • Determine if sentiment leads or lags price")
        print("  • Find sentiment reversal patterns")
        print("  • Correlate sentiment with earnings/announcements")
        
        print("\n📈 SIGNAL GENERATION LOGIC:")
        print("  • Score > +0.3 → Strong bullish sentiment signal")
        print("  • Score +0.1 to +0.3 → Moderate bullish signal")
        print("  • Score -0.1 to +0.1 → Neutral (no signal)")
        print("  • Score -0.3 to -0.1 → Moderate bearish signal")
        print("  • Score < -0.3 → Strong bearish sentiment signal")
        print("  • High article count → Increased weight/confidence")
        
        print("\n🔗 COMBINING WITH OTHER DATA:")
        print("  • Technical + Sentiment → Confirmation signals")
        print("  • Fundamental + Sentiment → Value + catalyst")
        print("  • Insider + Sentiment → Smart money + public sentiment")
        print("  • News + Scores → Understand why sentiment changed")
        
        print("\n📈 NEXT STEPS:")
        print("  1. Match sentiment spikes with financial news")
        print("  2. Correlate sentiment with price movements")
        print("  3. Identify predictive patterns")
        print("  4. Generate weighted sentiment signals")
        print("  5. Combine with other signals for final trade decision")
    
    return data


if __name__ == "__main__":
    results = main()
