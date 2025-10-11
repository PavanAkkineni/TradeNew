"""
Test API endpoints to verify data is loading correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_endpoints():
    """Test all API endpoints"""
    
    print("="*60)
    print("TESTING API ENDPOINTS")
    print("="*60)
    
    # Test overview
    print("\n1. Testing /api/overview/IBM")
    try:
        response = requests.get(f"{BASE_URL}/overview/IBM")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success - Price: ${data.get('current_price', {}).get('price', 'N/A')}")
            print(f"   Company: {data.get('name', 'N/A')}")
            print(f"   Market Cap: {data.get('key_stats', {}).get('market_cap', 'N/A')}")
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test technical
    print("\n2. Testing /api/technical/IBM")
    try:
        response = requests.get(f"{BASE_URL}/technical/IBM")
        if response.status_code == 200:
            data = response.json()
            indicators = data.get('indicators', {})
            print(f"✅ Success - RSI: {indicators.get('rsi', 'N/A')}")
            print(f"   Current Price: ${indicators.get('current_price', 'N/A')}")
            print(f"   Trend: {indicators.get('trend', 'N/A')}")
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test signals
    print("\n3. Testing /api/signals/IBM")
    try:
        response = requests.get(f"{BASE_URL}/signals/IBM")
        if response.status_code == 200:
            data = response.json()
            signal = data.get('signal', {})
            print(f"✅ Success - Signal: {signal.get('signal', 'N/A')}")
            print(f"   Strength: {signal.get('strength', 'N/A')}")
            print(f"   Confidence: {signal.get('confidence', 'N/A')}%")
        else:
            print(f"❌ Failed - Status: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_endpoints()
