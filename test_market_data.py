#!/usr/bin/env python3
"""
Test script for Market Data Aggregation Engine (Component 2)
"""
import requests
import json
import os

API_BASE = "http://localhost:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_api_keys():
    """Check which API keys are configured"""
    print_section("API Keys Configuration Check")
    
    keys = {
        'FRED_API_KEY': os.getenv('FRED_API_KEY'),
        'ALPHA_VANTAGE_API_KEY': os.getenv('ALPHA_VANTAGE_API_KEY'),
        'FINNHUB_API_KEY': os.getenv('FINNHUB_API_KEY'),
        'NEWS_API_KEY': os.getenv('NEWS_API_KEY')
    }
    
    for key_name, key_value in keys.items():
        status = "✅ Configured" if key_value else "❌ Not Set"
        if key_value:
            masked = key_value[:8] + "..." + key_value[-4:] if len(key_value) > 12 else key_value[:4] + "..."
            print(f"{key_name}: {status} ({masked})")
        else:
            print(f"{key_name}: {status}")

def test_endpoint(endpoint, name):
    """Test a specific endpoint"""
    print_section(f"Testing: {name}")
    print(f"Endpoint: {endpoint}")
    
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status: {response.status_code} OK")
            print(f"Response preview:")
            print(json.dumps(data, indent=2)[:500])
            
            # Check for errors in the data
            if 'metadata' in data and 'status' in data['metadata']:
                print(f"\n📊 Aggregation Status: {data['metadata']['status']}")
                if 'aggregation_duration_seconds' in data['metadata']:
                    print(f"⏱️  Duration: {data['metadata']['aggregation_duration_seconds']:.2f}s")
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_full_aggregation():
    """Test full market data aggregation and display summary"""
    print_section("Full Market Data Aggregation Test")
    
    try:
        response = requests.get(f"{API_BASE}/market-data", timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Full aggregation successful!")
            
            # Economic Indicators Summary
            print("\n📊 Economic Indicators:")
            econ = data.get('economic_indicators', {})
            for indicator, info in econ.items():
                value = info.get('value')
                if value is not None:
                    print(f"  • {indicator}: {value}")
                else:
                    error = info.get('error', 'No data')
                    print(f"  • {indicator}: ❌ {error}")
            
            # Market Performance Summary
            print("\n📈 Market Performance:")
            market = data.get('market_performance', {})
            for symbol, info in market.items():
                price = info.get('current_price')
                if price is not None:
                    print(f"  • {symbol}: ${price:.2f}")
                else:
                    error = info.get('error', 'No data')
                    print(f"  • {symbol}: ❌ {error}")
            
            # Market Sentiment Summary
            print("\n📰 Market Sentiment:")
            sentiment = data.get('market_sentiment', {})
            headlines = sentiment.get('headlines', [])
            if headlines:
                print(f"  • Found {len(headlines)} recent headlines")
                print(f"  • Latest: {headlines[0].get('title', 'N/A')}")
            else:
                error = sentiment.get('error', 'No data')
                print(f"  • ❌ {error}")
            
            # Metadata
            print("\n🔧 Metadata:")
            meta = data.get('metadata', {})
            print(f"  • Status: {meta.get('status', 'unknown')}")
            print(f"  • Duration: {meta.get('aggregation_duration_seconds', 0):.2f}s")
            print(f"  • API Keys: {meta.get('api_keys_configured', {})}")
            
            return True
        else:
            print(f"❌ Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MARKET DATA AGGREGATOR TEST" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # Check API keys
    check_api_keys()
    
    # Test individual endpoints
    tests = [
        ("/market-data/economic", "Economic Indicators"),
        ("/market-data/performance", "Market Performance"),
        ("/market-data/sentiment", "Market Sentiment"),
    ]
    
    results = []
    for endpoint, name in tests:
        result = test_endpoint(endpoint, name)
        results.append((name, result))
    
    # Test full aggregation
    full_result = test_full_aggregation()
    results.append(("Full Aggregation", full_result))
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Market Data Aggregator is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check API keys and connectivity.")
        print("See API_KEYS_SETUP.md for configuration instructions.")

if __name__ == "__main__":
    main()

