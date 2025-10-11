import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

# Get EODHD API key from environment variable
EODHD_API_KEY = os.getenv('EODHD_API_KEY')

if not EODHD_API_KEY:
    raise ValueError("EODHD API key not found. Please set EODHD_API_KEY in your .env file")

BASE_URL = 'https://eodhd.com/api/news'
SYMBOL = 'IBM.US'  # EODHD format

def fetch_financial_news(from_date=None, to_date=None, limit=1000, offset=0):
    """
    Fetch financial news for IBM from EODHD API.
    
    According to documentation, we need 90 days of news for sentiment analysis.
    
    Parameters:
    -----------
    from_date : str, optional
        Start date in YYYY-MM-DD format. Defaults to 90 days ago.
    to_date : str, optional
        End date in YYYY-MM-DD format. Defaults to today.
    limit : int
        Number of results (max 1000 per call)
    offset : int
        Pagination offset
    
    Returns:
    --------
    list : List of news articles
    """
    
    # Default to 90 days of news (recommended for sentiment analysis)
    if not from_date:
        from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    if not to_date:
        to_date = datetime.now().strftime('%Y-%m-%d')
    
    params = {
        's': SYMBOL,
        'from': from_date,
        'to': to_date,
        'limit': limit,
        'offset': offset,
        'api_token': EODHD_API_KEY,
        'fmt': 'json'
    }
    
    print(f"\nFetching financial news for {SYMBOL}...")
    print(f"Date range: {from_date} to {to_date}")
    print(f"Limit: {limit}, Offset: {offset}")
    print("-" * 60)
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if isinstance(data, list):
            print(f"✅ Retrieved {len(data)} news articles")
            return data
        else:
            print(f"⚠️ Unexpected response format: {type(data)}")
            return []
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return []


def analyze_news_data(articles):
    """Analyze the fetched news data and display summary."""
    
    if not articles:
        print("No articles to analyze")
        return
    
    print(f"\n📊 NEWS ANALYSIS:")
    print(f"Total articles: {len(articles)}")
    
    # Date range
    dates = [article.get('date', '')[:10] for article in articles if article.get('date')]
    if dates:
        print(f"Date range: {min(dates)} to {max(dates)}")
    
    # Sentiment analysis
    sentiments = [article.get('sentiment', {}) for article in articles if article.get('sentiment')]
    
    if sentiments:
        avg_polarity = sum(s.get('polarity', 0) for s in sentiments) / len(sentiments)
        avg_pos = sum(s.get('pos', 0) for s in sentiments) / len(sentiments)
        avg_neg = sum(s.get('neg', 0) for s in sentiments) / len(sentiments)
        avg_neu = sum(s.get('neu', 0) for s in sentiments) / len(sentiments)
        
        print(f"\n📈 SENTIMENT SUMMARY:")
        print(f"  Average Polarity: {avg_polarity:.3f} (range: -1 to +1)")
        print(f"  Average Positive: {avg_pos:.3f}")
        print(f"  Average Negative: {avg_neg:.3f}")
        print(f"  Average Neutral: {avg_neu:.3f}")
        
        # Categorize sentiment
        if avg_polarity > 0.5:
            sentiment_label = "🟢 BULLISH"
        elif avg_polarity > 0:
            sentiment_label = "🟡 SLIGHTLY BULLISH"
        elif avg_polarity > -0.5:
            sentiment_label = "🟠 SLIGHTLY BEARISH"
        else:
            sentiment_label = "🔴 BEARISH"
        
        print(f"\n  Overall Sentiment: {sentiment_label}")
    
    # Tag analysis
    all_tags = []
    for article in articles:
        tags = article.get('tags', [])
        all_tags.extend(tags)
    
    if all_tags:
        from collections import Counter
        tag_counts = Counter(all_tags)
        print(f"\n🏷️ TOP TAGS:")
        for tag, count in tag_counts.most_common(10):
            print(f"  {tag}: {count}")
    
    # Recent headlines
    print(f"\n📰 RECENT HEADLINES (top 5):")
    for i, article in enumerate(articles[:5]):
        date = article.get('date', 'N/A')[:10]
        title = article.get('title', 'N/A')
        polarity = article.get('sentiment', {}).get('polarity', 0)
        
        sentiment_icon = "🟢" if polarity > 0 else "🔴" if polarity < 0 else "⚪"
        print(f"\n  {i+1}. [{date}] {sentiment_icon} {title[:80]}...")
        print(f"     Polarity: {polarity:.3f}")


def save_to_file(articles, filename=None):
    """Save articles to JSON file."""
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_news_{timestamp}.json"
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    file_size = os.path.getsize(filepath)
    print(f"\n💾 Data saved to: {filename}")
    print(f"📦 File size: {file_size / 1024:.1f} KB")
    
    return filepath


def main():
    """
    Fetch 90 days of financial news for IBM.
    
    According to documentation:
    - Need 90 days for sentiment analysis
    - Each article includes sentiment scores (polarity, pos, neg, neu)
    - Maximum 1000 articles per call
    """
    
    print("=" * 60)
    print("FETCHING FINANCIAL NEWS FOR IBM")
    print("=" * 60)
    print("Source: EODHD Financial News API")
    print("Target: 90 days of news articles")
    print("=" * 60)
    
    # Calculate date range (90 days)
    to_date = datetime.now().strftime('%Y-%m-%d')
    from_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Fetch news (may need multiple calls if more than 1000 articles)
    all_articles = []
    offset = 0
    limit = 1000
    
    while True:
        articles = fetch_financial_news(from_date, to_date, limit, offset)
        
        if not articles:
            break
        
        all_articles.extend(articles)
        
        # If we got fewer articles than the limit, we're done
        if len(articles) < limit:
            break
        
        # Otherwise, fetch more with pagination
        offset += limit
        print(f"\n⏳ Fetching more articles (offset: {offset})...")
        time.sleep(1)  # Rate limiting
    
    print(f"\n{'='*60}")
    print(f"📊 TOTAL ARTICLES FETCHED: {len(all_articles)}")
    print(f"{'='*60}")
    
    if all_articles:
        # Analyze the data
        analyze_news_data(all_articles)
        
        # Save to file
        save_to_file(all_articles)
        
        print("\n" + "=" * 60)
        print("📊 FINANCIAL NEWS FETCH COMPLETE")
        print("=" * 60)
        
        print("\n🎯 USE CASES:")
        print("  • Catalyst identification (earnings, announcements)")
        print("  • Sentiment trend analysis (bullish/bearish shifts)")
        print("  • Event-driven trading (news-based signals)")
        print("  • Correlation with price movements")
        print("  • Risk identification (negative news clusters)")
        
        print("\n💡 RELATIONSHIP WITH SENTIMENT SCORES:")
        print("  • News articles → Daily aggregated sentiment scores")
        print("  • High sentiment score → Check news for specific catalysts")
        print("  • Low sentiment score → Identify risk factors in news")
        print("  • Sentiment spikes → Major events or announcements")
        print("  • Use news to explain sentiment score changes")
        
        print("\n📈 NEXT STEPS:")
        print("  1. Fetch historical sentiment scores (sentiments API)")
        print("  2. Match sentiment spikes with news events")
        print("  3. Identify which types of news drive signals")
        print("  4. Generate sentiment-based trade signals")
    
    return all_articles


if __name__ == "__main__":
    results = main()
