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

def fetch_insider_transactions():
    """
    Fetch insider transactions for IBM.
    Returns historical insider transactions (12+ months recommended).
    
    Returns:
    --------
    dict : JSON response from API
    """
    params = {
        'function': 'INSIDER_TRANSACTIONS',
        'symbol': SYMBOL,
        'apikey': API_KEY
    }
    
    print(f"\nFetching insider transactions for {SYMBOL}...")
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
            return fetch_insider_transactions()
        
        if "Information" in data and "premium" in data.get("Information", "").lower():
            print(f"⚠️ Premium endpoint: {data['Information']}")
            return data
        
        # Save to file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"insider_transactions_{timestamp}.json"
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Data saved to: {filename}")
        print(f"📦 File size: {file_size / 1024:.1f} KB")
        
        # Analyze the data
        analyze_insider_data(data)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None


def analyze_insider_data(data):
    """Analyze insider transaction data and display summary."""
    
    if 'data' not in data:
        print("⚠️ No transaction data found")
        return
    
    transactions = data['data']
    print(f"\n📊 Total Transactions: {len(transactions)}")
    
    if not transactions:
        print("No insider transactions available")
        return
    
    # Analyze by transaction type
    buys = [t for t in transactions if 'acquisition' in t.get('transaction_type', '').lower() or 'buy' in t.get('transaction_type', '').lower()]
    sells = [t for t in transactions if 'sale' in t.get('transaction_type', '').lower() or 'sell' in t.get('transaction_type', '').lower()]
    
    print(f"\n📈 Buy Transactions: {len(buys)}")
    print(f"📉 Sell Transactions: {len(sells)}")
    
    # Calculate total values
    total_buy_value = 0
    total_sell_value = 0
    
    for t in buys:
        try:
            shares = float(t.get('securities_transacted', 0))
            price = float(t.get('security_price', 0))
            total_buy_value += shares * price
        except (ValueError, TypeError):
            pass
    
    for t in sells:
        try:
            shares = float(t.get('securities_transacted', 0))
            price = float(t.get('security_price', 0))
            total_sell_value += shares * price
        except (ValueError, TypeError):
            pass
    
    print(f"\n💰 Total Buy Value: ${total_buy_value:,.2f}")
    print(f"💰 Total Sell Value: ${total_sell_value:,.2f}")
    print(f"📊 Net Position: ${total_buy_value - total_sell_value:,.2f}")
    
    # Most recent transactions
    print("\n🔍 Most Recent Transactions:")
    for i, t in enumerate(transactions[:5]):
        trans_type = t.get('transaction_type', 'N/A')
        date = t.get('transaction_date', 'N/A')
        insider = t.get('insider_name', 'N/A')
        shares = t.get('securities_transacted', 'N/A')
        price = t.get('security_price', 'N/A')
        
        print(f"\n  {i+1}. {trans_type}")
        print(f"     Date: {date}")
        print(f"     Insider: {insider}")
        print(f"     Shares: {shares}")
        print(f"     Price: ${price}")
    
    # Signal interpretation
    print("\n📊 SIGNAL INTERPRETATION:")
    if total_buy_value > total_sell_value:
        net = total_buy_value - total_sell_value
        print(f"  ✅ NET BULLISH - Insiders buying ${net:,.2f} more than selling")
        if net > 1_000_000:
            print(f"  🚀 STRONG SIGNAL - Over $1M net buying")
    elif total_sell_value > total_buy_value:
        net = total_sell_value - total_buy_value
        print(f"  ⚠️ NET BEARISH - Insiders selling ${net:,.2f} more than buying")
        if net > 5_000_000:
            print(f"  🔴 STRONG SIGNAL - Over $5M net selling")
    else:
        print(f"  ➖ NEUTRAL - Equal buying and selling")


def main():
    """Main function to fetch and analyze insider transactions."""
    
    print("=" * 60)
    print("FETCHING INSIDER TRANSACTIONS FOR MSFT")
    print("=" * 60)
    print("Target: 12+ months of insider activity")
    print("Purpose: Smart money tracking (Alternative Data)")
    print("=" * 60)
    
    data = fetch_insider_transactions()
    
    if data:
        print("\n" + "=" * 60)
        print("📊 INSIDER TRANSACTIONS FETCH COMPLETE")
        print("=" * 60)
        
        print("\n🎯 Use Cases:")
        print("  • Smart money tracking (executives' confidence)")
        print("  • Cluster analysis (multiple insiders buying)")
        print("  • Timing analysis (unusual activity before events)")
        print("  • Signal generation (buy/sell/hold)")
        
        print("\n💡 Key Insights:")
        print("  • Insider BUYING = High confidence signal")
        print("  • Multiple executives buying = Strongest signal")
        print("  • Large purchases (>$1M) = Very significant")
        print("  • Selling can be for many reasons (less reliable)")
        
        print("\n📈 Next Steps:")
        print("  1. Compare with historical patterns")
        print("  2. Weight by transaction size")
        print("  3. Identify clusters (multiple insiders)")
        print("  4. Generate alternative data signal")
    
    return data


if __name__ == "__main__":
    results = main()
