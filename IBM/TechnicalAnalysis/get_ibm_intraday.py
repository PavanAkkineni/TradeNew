import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from parent directory
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(parent_dir, '.env'))

def get_ibm_intraday_data(interval='5min', outputsize='full', adjusted=True, extended_hours=False):
    """
    Fetch intraday data for IBM stock from Alpha Vantage API.
    
    Parameters:
    -----------
    interval : str
        Time interval between data points. Options: '1min', '5min', '15min', '30min', '60min'
        Default: '5min'
    outputsize : str
        'compact' for last 100 data points, 'full' for last 30 days
        Default: 'full'
    adjusted : bool
        If True, data is adjusted for splits/dividends. Default: True
    extended_hours : bool
        If True, includes pre-market and post-market data. Default: False
        
    Returns:
    --------
    dict : JSON response from Alpha Vantage API
    """
    
    # Get API key from environment variable
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    
    if not api_key:
        raise ValueError("API key not found. Please set ALPHA_VANTAGE_API_KEY in your .env file")
    
    # Build the API URL
    base_url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_INTRADAY',
        'symbol': 'IBM',
        'interval': interval,
        'outputsize': outputsize,
        'adjusted': str(adjusted).lower(),
        'extended_hours': str(extended_hours).lower(),
        'apikey': api_key
    }
    
    print(f"Fetching IBM intraday data...")
    print(f"Symbol: IBM")
    print(f"Interval: {interval}")
    print(f"Output size: {outputsize} (last 30 days)")
    print(f"Adjusted: {adjusted}")
    print(f"Extended hours: {extended_hours}")
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
        if f"Time Series ({interval})" in data:
            time_series = data[f"Time Series ({interval})"]
            print(f"✅ Successfully retrieved {len(time_series)} data points")
            
            # Get the date range
            timestamps = list(time_series.keys())
            if timestamps:
                latest = timestamps[0]
                oldest = timestamps[-1]
                print(f"Date range: {oldest} to {latest}")
                
                # Display sample data (first entry)
                print("\nSample data (most recent):")
                print(f"Timestamp: {latest}")
                for key, value in time_series[latest].items():
                    print(f"  {key}: {value}")
        
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
        filename = f"ibm_intraday_{timestamp}.json"
    
    # Save in the same directory as this script (Intraday folder)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Data saved to: {filepath}")
    return filepath


def main():
    """Main function to fetch and save IBM intraday data."""
    try:
        # Fetch data for last 30 days with 5-minute intervals
        # Regular trading hours only (no extended hours)
        data = get_ibm_intraday_data(
            interval='5min',
            outputsize='full',  # Gets last 30 days
            adjusted=True,      # Adjusted for splits/dividends
            extended_hours=False  # Regular trading hours only (9:30am - 4:00pm ET)
        )
        
        # Save to file
        save_data_to_file(data)
        
        print("\n✅ Done! Data fetched and saved successfully.")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
