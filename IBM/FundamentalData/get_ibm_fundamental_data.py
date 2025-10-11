import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
import time

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

# Get API key from environment variable
API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')

if not API_KEY:
    raise ValueError("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file")

BASE_URL = 'https://www.alphavantage.co/query'
SYMBOL = 'IBM'

def fetch_and_save(function_name, filename, additional_params=None):
    """
    Generic function to fetch data from Alpha Vantage and save to file.
    
    Parameters:
    -----------
    function_name : str
        The Alpha Vantage function to call
    filename : str
        The filename to save the data
    additional_params : dict, optional
        Additional parameters for the API call
    
    Returns:
    --------
    dict : JSON response from API
    """
    params = {
        'function': function_name,
        'symbol': SYMBOL,
        'apikey': API_KEY
    }
    
    if additional_params:
        params.update(additional_params)
    
    print(f"\nFetching {function_name} for {SYMBOL}...")
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
            return fetch_and_save(function_name, filename, additional_params)
        
        if "Information" in data and "premium" in data["Information"].lower():
            print(f"⚠️ Premium endpoint: {data['Information']}")
            return data
        
        # Save to file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(script_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        file_size = os.path.getsize(filepath)
        print(f"✅ Data saved to: {filename}")
        print(f"📦 File size: {file_size / 1024:.1f} KB")
        
        # Display key information
        display_data_summary(function_name, data)
        
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")
        return None


def display_data_summary(function_name, data):
    """Display summary information about the fetched data."""
    
    if function_name == 'OVERVIEW':
        if 'Symbol' in data:
            print(f"Company: {data.get('Name', 'N/A')}")
            print(f"Sector: {data.get('Sector', 'N/A')}")
            print(f"Industry: {data.get('Industry', 'N/A')}")
            print(f"Market Cap: ${float(data.get('MarketCapitalization', 0))/1e9:.2f}B")
            print(f"P/E Ratio: {data.get('PERatio', 'N/A')}")
            print(f"Dividend Yield: {data.get('DividendYield', 'N/A')}")
    
    elif function_name == 'INCOME_STATEMENT':
        annual = data.get('annualReports', [])
        quarterly = data.get('quarterlyReports', [])
        print(f"Annual reports: {len(annual)}")
        print(f"Quarterly reports: {len(quarterly)}")
        if annual:
            latest = annual[0]
            print(f"Latest annual: {latest.get('fiscalDateEnding', 'N/A')}")
            print(f"  Revenue: ${float(latest.get('totalRevenue', 0))/1e9:.2f}B")
            print(f"  Net Income: ${float(latest.get('netIncome', 0))/1e9:.2f}B")
    
    elif function_name == 'BALANCE_SHEET':
        annual = data.get('annualReports', [])
        quarterly = data.get('quarterlyReports', [])
        print(f"Annual reports: {len(annual)}")
        print(f"Quarterly reports: {len(quarterly)}")
        if annual:
            latest = annual[0]
            print(f"Latest annual: {latest.get('fiscalDateEnding', 'N/A')}")
            print(f"  Total Assets: ${float(latest.get('totalAssets', 0))/1e9:.2f}B")
            print(f"  Total Liabilities: ${float(latest.get('totalLiabilities', 0))/1e9:.2f}B")
    
    elif function_name == 'CASH_FLOW':
        annual = data.get('annualReports', [])
        quarterly = data.get('quarterlyReports', [])
        print(f"Annual reports: {len(annual)}")
        print(f"Quarterly reports: {len(quarterly)}")
        if annual:
            latest = annual[0]
            print(f"Latest annual: {latest.get('fiscalDateEnding', 'N/A')}")
            print(f"  Operating Cash Flow: ${float(latest.get('operatingCashflow', 0))/1e9:.2f}B")
    
    elif function_name == 'DIVIDENDS':
        dividends = data.get('data', [])
        print(f"Dividend records: {len(dividends)}")
        if dividends:
            print(f"Most recent: {dividends[0].get('ex_dividend_date', 'N/A')} - ${dividends[0].get('amount', 'N/A')}")
    
    elif function_name == 'SPLITS':
        splits = data.get('data', [])
        print(f"Split records: {len(splits)}")
        if splits:
            print(f"Most recent: {splits[0].get('effective_date', 'N/A')} - {splits[0].get('split_factor', 'N/A')}")
    
    elif function_name == 'EARNINGS':
        annual = data.get('annualEarnings', [])
        quarterly = data.get('quarterlyEarnings', [])
        print(f"Annual earnings: {len(annual)}")
        print(f"Quarterly earnings: {len(quarterly)}")
        if quarterly:
            latest = quarterly[0]
            print(f"Latest quarter: {latest.get('fiscalDateEnding', 'N/A')}")
            print(f"  Reported EPS: ${latest.get('reportedEPS', 'N/A')}")
            print(f"  Estimated EPS: ${latest.get('estimatedEPS', 'N/A')}")
            print(f"  Surprise: ${latest.get('surprise', 'N/A')}")
    
    elif function_name == 'EARNINGS_ESTIMATES':
        if 'quarterlyEstimates' in data:
            print(f"Quarterly estimates: {len(data.get('quarterlyEstimates', []))}")
        if 'annualEstimates' in data:
            print(f"Annual estimates: {len(data.get('annualEstimates', []))}")
    
    elif function_name == 'SHARES_OUTSTANDING':
        shares_data = data.get('data', [])
        print(f"Quarterly records: {len(shares_data)}")
        if shares_data:
            latest = shares_data[0]
            print(f"Latest: {latest.get('date', 'N/A')}")
            print(f"  Shares Outstanding: {float(latest.get('sharesOutstanding', 0))/1e9:.2f}B")


def main():
    """Fetch all fundamental data for IBM."""
    
    print("=" * 60)
    print("FETCHING FUNDAMENTAL DATA FOR IBM")
    print("=" * 60)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Define all endpoints to fetch
    endpoints = [
        # Company Overview
        {
            'function': 'OVERVIEW',
            'filename': f'company_overview_{timestamp}.json',
            'description': 'Company information and key metrics'
        },
        
        # Financial Statements (Need 5 years = 20 quarters)
        {
            'function': 'INCOME_STATEMENT',
            'filename': f'income_statement_{timestamp}.json',
            'description': 'Annual & quarterly income statements'
        },
        {
            'function': 'BALANCE_SHEET',
            'filename': f'balance_sheet_{timestamp}.json',
            'description': 'Annual & quarterly balance sheets'
        },
        {
            'function': 'CASH_FLOW',
            'filename': f'cash_flow_{timestamp}.json',
            'description': 'Annual & quarterly cash flow statements'
        },
        
        # Corporate Actions
        {
            'function': 'DIVIDENDS',
            'filename': f'dividends_{timestamp}.json',
            'description': 'Historical and future dividends'
        },
        {
            'function': 'SPLITS',
            'filename': f'splits_{timestamp}.json',
            'description': 'Stock split history'
        },
        
        # Shares Outstanding
        {
            'function': 'SHARES_OUTSTANDING',
            'filename': f'shares_outstanding_{timestamp}.json',
            'description': 'Quarterly shares outstanding'
        },
        
        # Earnings Data (Need 8+ quarters)
        {
            'function': 'EARNINGS',
            'filename': f'earnings_history_{timestamp}.json',
            'description': 'Annual & quarterly earnings history'
        },
        {
            'function': 'EARNINGS_ESTIMATES',
            'filename': f'earnings_estimates_{timestamp}.json',
            'description': 'EPS and revenue estimates'
        },
    ]
    
    results = {}
    successful = 0
    failed = 0
    
    for endpoint in endpoints:
        print(f"\n{'='*60}")
        print(f"📊 {endpoint['description']}")
        print(f"{'='*60}")
        
        data = fetch_and_save(
            endpoint['function'],
            endpoint['filename']
        )
        
        if data:
            results[endpoint['function']] = {
                'status': 'success',
                'filename': endpoint['filename']
            }
            successful += 1
        else:
            results[endpoint['function']] = {
                'status': 'failed',
                'filename': endpoint['filename']
            }
            failed += 1
        
        # Rate limiting: wait 12 seconds between calls (free tier: 5 calls/minute)
        if endpoint != endpoints[-1]:  # Don't wait after last call
            print("\n⏳ Waiting 12 seconds (rate limiting)...")
            time.sleep(12)
    
    # Final summary
    print("\n" + "=" * 60)
    print("📊 FUNDAMENTAL DATA FETCH COMPLETE")
    print("=" * 60)
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total files: {successful}")
    
    print("\n📋 Data Coverage:")
    print("  • Company Overview: Current snapshot")
    print("  • Income Statement: 5 years (annual + quarterly)")
    print("  • Balance Sheet: 5 years (annual + quarterly)")
    print("  • Cash Flow: 5 years (annual + quarterly)")
    print("  • Dividends: Complete history")
    print("  • Splits: Complete history")
    print("  • Shares Outstanding: Quarterly data")
    print("  • Earnings History: Annual + quarterly (with estimates)")
    print("  • Earnings Estimates: Forward estimates")
    
    print("\n🎯 Next Steps:")
    print("  1. Review the fetched data")
    print("  2. Calculate financial ratios (P/E, ROE, Debt/Equity)")
    print("  3. Analyze trends (revenue growth, margin expansion)")
    print("  4. Combine with technical signals for final trade signal")
    
    return results


if __name__ == "__main__":
    results = main()
