import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(root_dir, '.env'))

API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if not API_KEY:
    raise ValueError("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file")

BASE_URL = 'https://www.alphavantage.co/query'
SYMBOL = 'MSFT'

def fetch_earnings_transcript(quarter):
    """
    Fetch earnings call transcript for a specific quarter.
    
    Parameters:
    -----------
    quarter : str
        Quarter in YYYYQM format (e.g., '2024Q1')
    
    Returns:
    --------
    dict : JSON response from API
    """
    params = {
        'function': 'EARNINGS_CALL_TRANSCRIPT',
        'symbol': SYMBOL,
        'quarter': quarter,
        'apikey': API_KEY
    }
    
    print(f"\nFetching earnings call transcript for {SYMBOL} - {quarter}...")
    print("-" * 60)
    
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            print(f"❌ API Error: {data['Error Message']}")
            return None
        
        if "Note" in data:
            print(f"⚠️ API Note: {data['Note']}")
            print("Rate limit hit. Waiting 60 seconds...")
            time.sleep(60)
            return fetch_earnings_transcript(quarter)
        
        if "Information" in data and "premium" in data.get("Information", "").lower():
            print(f"⚠️ Premium endpoint: {data['Information']}")
            return data
        
        # Save to file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"earnings_transcript_{quarter}.json"
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Data saved to: {filename}")
        print(f"📦 File size: {file_size / 1024:.1f} KB")
        
        # Display summary
        if 'content' in data:
            content_length = len(data['content'])
            print(f"📄 Transcript length: {content_length:,} characters")
            
            # Show first 200 characters
            preview = data['content'][:200].replace('\n', ' ')
            print(f"Preview: {preview}...")
        
        if 'sentiment_analysis' in data:
            sentiment = data['sentiment_analysis']
            print(f"📊 Sentiment Score: {sentiment.get('overall_sentiment', 'N/A')}")
            print(f"📊 Confidence: {sentiment.get('confidence', 'N/A')}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None


def main():
    """
    Fetch earnings call transcripts for the last 8 quarters.
    According to documentation, we need 8 quarters (2 years) for sentiment analysis.
    """
    
    print("=" * 60)
    print("FETCHING EARNINGS CALL TRANSCRIPTS FOR MSFT")
    print("=" * 60)
    print("Target: Last 8 quarters (2 years)")
    print("=" * 60)
    
    # Define quarters to fetch (last 8 quarters from Q3 2025)
    # Going back 2 years from Q3 2025
    quarters = [
        '2025Q3',  # Q3 2025
        '2025Q2',  # Q2 2025
        '2025Q1',  # Q1 2025
        '2024Q4',  # Q4 2024
        '2024Q3',  # Q3 2024
        '2024Q2',  # Q2 2024
        '2024Q1',  # Q1 2024
        '2023Q4',  # Q4 2023
    ]
    
    results = {}
    successful = 0
    failed = 0
    
    for quarter in quarters:
        data = fetch_earnings_transcript(quarter)
        
        if data:
            results[quarter] = 'success'
            successful += 1
        else:
            results[quarter] = 'failed'
            failed += 1
        
        # Rate limiting: wait 12 seconds between calls
        if quarter != quarters[-1]:
            print("\n⏳ Waiting 12 seconds (rate limiting)...")
            time.sleep(12)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 EARNINGS CALL TRANSCRIPTS FETCH COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    
    print("\n📋 Fetched Quarters:")
    for quarter, status in results.items():
        status_icon = "✅" if status == "success" else "❌"
        print(f"  {status_icon} {quarter}")
    
    print("\n🎯 Use Cases:")
    print("  • Sentiment analysis (management confidence)")
    print("  • Guidance extraction (forward-looking statements)")
    print("  • Risk identification (cautionary language)")
    print("  • Strategy changes (business model shifts)")
    print("  • FinLLM integration (deep analysis)")
    
    print("\n💡 Next Steps:")
    print("  1. Use FinLLM to analyze transcript sentiment")
    print("  2. Extract key themes and concerns")
    print("  3. Compare quarter-over-quarter tone changes")
    print("  4. Generate sentiment signals for aggregation")
    
    return results


if __name__ == "__main__":
    results = main()
