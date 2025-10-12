import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(root_dir, '.env'))

# Get EODHD API key
API_KEY = os.getenv('EODHD_API_KEY')

if not API_KEY:
    raise ValueError("EODHD API key not found. Please set EODHD_API_KEY in your .env file")

SYMBOL = 'MSFT.US'  # EODHD format
BASE_URL = 'https://eodhd.com/api'

def fetch_fundamentals():
    """
    Fetch fundamental data from EODHD API.
    EODHD provides comprehensive fundamental data without strict rate limits.
    """
    
    print("=" * 60)
    print("FETCHING FUNDAMENTAL DATA FOR MSFT (via EODHD)")
    print("=" * 60)
    
    url = f"{BASE_URL}/fundamentals/{SYMBOL}"
    params = {
        'api_token': API_KEY,
        'fmt': 'json'
    }
    
    print(f"\nFetching comprehensive fundamental data for {SYMBOL}...")
    print("-" * 60)
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if we got actual data
        if not data or 'General' not in data:
            print(f"❌ No fundamental data available")
            return None
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"msft_fundamentals_eodhd_{timestamp}.json"
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Data saved to: {filename}")
        print(f"📦 File size: {file_size / 1024:.1f} KB")
        
        # Display summary
        display_summary(data)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None


def display_summary(data):
    """Display summary of fetched fundamental data."""
    
    print("\n" + "=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    
    # General Information
    if 'General' in data:
        general = data['General']
        print("\n📊 COMPANY OVERVIEW:")
        print(f"  Name: {general.get('Name', 'N/A')}")
        print(f"  Sector: {general.get('Sector', 'N/A')}")
        print(f"  Industry: {general.get('Industry', 'N/A')}")
        print(f"  Exchange: {general.get('Exchange', 'N/A')}")
        print(f"  Country: {general.get('CountryName', 'N/A')}")
    
    # Highlights (Key Metrics)
    if 'Highlights' in data:
        highlights = data['Highlights']
        print("\n💡 KEY METRICS:")
        print(f"  Market Cap: ${float(highlights.get('MarketCapitalization', 0))/1e9:.2f}B")
        print(f"  P/E Ratio: {highlights.get('PERatio', 'N/A')}")
        print(f"  EPS: ${highlights.get('EarningsShare', 'N/A')}")
        print(f"  Dividend Yield: {highlights.get('DividendYield', 'N/A')}")
        print(f"  52 Week High: ${highlights.get('52WeekHigh', 'N/A')}")
        print(f"  52 Week Low: ${highlights.get('52WeekLow', 'N/A')}")
    
    # Valuation
    if 'Valuation' in data:
        valuation = data['Valuation']
        print("\n📈 VALUATION:")
        print(f"  Trailing P/E: {valuation.get('TrailingPE', 'N/A')}")
        print(f"  Forward P/E: {valuation.get('ForwardPE', 'N/A')}")
        print(f"  Price to Book: {valuation.get('PriceBookMRQ', 'N/A')}")
        print(f"  Price to Sales: {valuation.get('PriceSalesTTM', 'N/A')}")
    
    # Financials - Income Statement
    if 'Financials' in data and 'Income_Statement' in data['Financials']:
        income_stmt = data['Financials']['Income_Statement']
        if 'yearly' in income_stmt and income_stmt['yearly']:
            latest_year = list(income_stmt['yearly'].keys())[0]
            latest_data = income_stmt['yearly'][latest_year]
            
            print("\n💰 LATEST ANNUAL FINANCIALS:")
            print(f"  Year: {latest_year}")
            print(f"  Revenue: ${float(latest_data.get('totalRevenue', 0))/1e9:.2f}B")
            print(f"  Gross Profit: ${float(latest_data.get('grossProfit', 0))/1e9:.2f}B")
            print(f"  Net Income: ${float(latest_data.get('netIncome', 0))/1e9:.2f}B")
            print(f"  Operating Income: ${float(latest_data.get('operatingIncome', 0))/1e9:.2f}B")
    
    # Balance Sheet
    if 'Financials' in data and 'Balance_Sheet' in data['Financials']:
        balance_sheet = data['Financials']['Balance_Sheet']
        if 'yearly' in balance_sheet and balance_sheet['yearly']:
            latest_year = list(balance_sheet['yearly'].keys())[0]
            latest_data = balance_sheet['yearly'][latest_year]
            
            print("\n📋 BALANCE SHEET:")
            print(f"  Total Assets: ${float(latest_data.get('totalAssets', 0))/1e9:.2f}B")
            print(f"  Total Liabilities: ${float(latest_data.get('totalLiab', 0))/1e9:.2f}B")
            print(f"  Total Equity: ${float(latest_data.get('totalStockholderEquity', 0))/1e9:.2f}B")
    
    # Cash Flow
    if 'Financials' in data and 'Cash_Flow' in data['Financials']:
        cash_flow = data['Financials']['Cash_Flow']
        if 'yearly' in cash_flow and cash_flow['yearly']:
            latest_year = list(cash_flow['yearly'].keys())[0]
            latest_data = cash_flow['yearly'][latest_year]
            
            print("\n💵 CASH FLOW:")
            print(f"  Operating Cash Flow: ${float(latest_data.get('totalCashFromOperatingActivities', 0))/1e9:.2f}B")
            print(f"  Investing Cash Flow: ${float(latest_data.get('totalCashflowsFromInvestingActivities', 0))/1e9:.2f}B")
            print(f"  Financing Cash Flow: ${float(latest_data.get('totalCashFromFinancingActivities', 0))/1e9:.2f}B")
    
    # Earnings History
    if 'Earnings' in data and 'History' in data['Earnings']:
        earnings_history = data['Earnings']['History']
        print(f"\n📊 EARNINGS HISTORY:")
        print(f"  Total quarters available: {len(earnings_history)}")
        if earnings_history:
            latest = list(earnings_history.values())[0]
            print(f"  Latest EPS: ${latest.get('epsActual', 'N/A')}")
            print(f"  Estimated EPS: ${latest.get('epsEstimate', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✅ EODHD provides comprehensive fundamental data including:")
    print("  • Company Overview & General Info")
    print("  • Financial Statements (Income, Balance Sheet, Cash Flow)")
    print("  • Earnings History & Estimates")
    print("  • Valuation Metrics")
    print("  • Key Ratios & Highlights")
    print("  • Analyst Recommendations")
    print("  • Insider Transactions")
    print("  • And much more!")
    print("=" * 60)


if __name__ == "__main__":
    result = fetch_fundamentals()
    
    if result:
        print("\n✅ Success! Fundamental data fetched and saved.")
    else:
        print("\n❌ Failed to fetch fundamental data.")
