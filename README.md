# Trade Signal Data Fetcher

This project fetches various types of stock market data using the Alpha Vantage API. Data is organized into separate folders by type for easy management and future use.

## Project Structure

```
TradeSignal/
├── Intraday/              # Intraday data (current implementation)
│   ├── get_ibm_intraday.py
│   └── *.json            # Output files
├── Daily/                # Daily adjusted data (future)
├── Weekly/               # Weekly adjusted data (future)
├── .env                  # API key configuration
├── .gitignore
├── requirements.txt
└── README.md
```

## Features

- ✅ **Organized data structure** - Each data type in its own folder
- ✅ **Intraday data** - Last 30 days with 5-minute intervals
- ✅ **Adjusted data** - Accounts for splits and dividends
- ✅ **Regular trading hours** - 9:30am - 4:00pm ET
- ✅ **Auto-save** - JSON files with timestamps
- ✅ **Secure** - API key in environment variables

## Prerequisites

- Python 3.7 or higher
- Alpha Vantage API key

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Key Configuration

Your API key is already configured in the `.env` file.

⚠️ **Important**: Never commit your `.env` file to version control.

## Usage

### Intraday Data (5-minute intervals, last 30 days)

```bash
cd Intraday
python get_ibm_intraday.py
```

**Output:**
- Data saved in `Intraday/` folder
- Filename format: `ibm_intraday_YYYYMMDD_HHMMSS.json`

**Current Configuration:**
- Symbol: IBM
- Interval: 5 minutes
- Time period: Last 30 days
- Adjusted: Yes (for splits/dividends)
- Extended hours: No (regular trading hours only)

### Future Data Types

Additional scripts will be added for:
- **Daily adjusted data** - In `Daily/` folder
- **Weekly adjusted data** - In `Weekly/` folder

## Output Format

JSON files contain OHLCV data (Open, High, Low, Close, Volume):

```json
{
  "Meta Data": {
    "1. Information": "Intraday (5min) open, high, low, close prices and volume",
    "2. Symbol": "IBM",
    "3. Last Refreshed": "2025-10-01 16:00:00",
    "4. Interval": "5min",
    "5. Output Size": "Full size",
    "6. Time Zone": "US/Eastern"
  },
  "Time Series (5min)": {
    "2025-10-01 16:00:00": {
      "1. open": "150.00",
      "2. high": "150.50",
      "3. low": "149.75",
      "4. close": "150.25",
      "5. volume": "12345"
    }
  }
}
```

## Rate Limits

⚠️ **Free API Key Limits**:
- 25 requests per day
- 5 requests per minute

Wait 1 minute between requests if you hit the rate limit.

## Troubleshooting

### API Key Issues
- Verify `.env` file exists in the root directory
- Check format: `ALPHA_VANTAGE_API_KEY=your_key_here`
- No spaces around the `=` sign

### Rate Limit
If you see "Thank you for using Alpha Vantage!", wait 1 minute before retrying.

### No Data
- Check internet connection
- Verify API key is valid
- Market data updates at end of trading day

## Files

- **`Intraday/get_ibm_intraday.py`** - Fetch intraday data
- **`requirements.txt`** - Python dependencies
- **`.env`** - Your API key (not tracked in git)
- **`.gitignore`** - Protects sensitive files

## License

MIT License
