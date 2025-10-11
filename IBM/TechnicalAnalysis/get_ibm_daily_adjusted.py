import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(root_dir, '.env'))

def get_ibm_daily_adjusted():
    """
    Fetch daily adjusted data for IBM stock from Alpha Vantage API.
    Gets full historical data (20+ years available, we need 2 years minimum).
    
    Returns:
    --------
    dict : JSON response from Alpha Vantage API
    """
    
    # Get API key from environment variable
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        raise ValueError("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file")
    
    # Build the API URL
    # Note: 'full' is premium endpoint, using 'compact' for free tier (100 data points ~4-5 months)
    # For full 2 years, you would need premium subscription
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol': 'IBM',
        'outputsize': 'compact',  # Get most recent 100 data points (free tier)
        'apikey': api_key
    }
    
    print(f"Fetching IBM Daily Adjusted data...")
    print(f"Symbol: IBM")
    print(f"Output size: Compact (most recent 100 data points)")
    print(f"Note: Full historical data requires premium subscription")
    print(f"Target: 2 years minimum (504 days) - using available data")
    print("-" * 50)
    
    try:
        # Make the API request
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for API errors
        if "Error Message" in data:
            raise Exception(f"API Error: {data['Error Message']}")
        
        if "Note" in data:
            print(f"⚠️ API Note: {data['Note']}")
            print("You may have hit the API rate limit. Consider waiting a minute before retrying.")
            return data
        
        # Display summary information
        if "Time Series (Daily)" in data:
            time_series = data["Time Series (Daily)"]
            print(f"✅ Successfully retrieved {len(time_series)} daily data points")
            
            # Get the date range
            dates = list(time_series.keys())
            if dates:
                latest = dates[0]
                oldest = dates[-1]
                print(f"Date range: {oldest} to {latest}")
                
                # Calculate years of data
                from datetime import datetime
                latest_date = datetime.strptime(latest, "%Y-%m-%d")
                oldest_date = datetime.strptime(oldest, "%Y-%m-%d")
                years = (latest_date - oldest_date).days / 365.25
                print(f"Years of data: {years:.1f} years")
                
                # Display sample data (most recent)
                print("\nSample data (most recent):")
                print(f"Date: {latest}")
                sample = time_series[latest]
                print(f"  Open: {sample['1. open']}")
                print(f"  High: {sample['2. high']}")
                print(f"  Low: {sample['3. low']}")
                print(f"  Close: {sample['4. close']}")
                print(f"  Adjusted Close: {sample['5. adjusted close']}")
                print(f"  Volume: {sample['6. volume']}")
                print(f"  Dividend: {sample['7. dividend amount']}")
                print(f"  Split Coefficient: {sample['8. split coefficient']}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {str(e)}")


def save_data_to_file(data, filename=None):
    """
    Save the fetched data to a JSON file in the current directory.
    
    Parameters:
    -----------
    data : dict
        The data to save
    filename : str, optional
        Custom filename. If None, generates timestamp-based filename
    """
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ibm_daily_adjusted_{timestamp}.json"
    
    # Save in the same directory as this script (Daily folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Data saved to: {filepath}")
    
    # Get file size
    file_size = os.path.getsize(filepath)
    print(f"📦 File size: {file_size / 1024:.1f} KB")
    
    return filepath


def main():
    """Main function to fetch and save IBM daily adjusted data."""
    try:
        # Fetch full historical data
        data = get_ibm_daily_adjusted()
        
        # Save to file
        save_data_to_file(data)
        
        print("\n✅ Done! Daily adjusted data fetched and saved successfully.")
        print("📊 This data includes:")
        print("   - OHLC (Open, High, Low, Close)")
        print("   - Adjusted Close (for splits & dividends)")
        print("   - Volume")
        print("   - Dividend amounts")
        print("   - Split coefficients")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
