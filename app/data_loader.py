"""
Data Loader Module
Loads and manages data from various folders
"""
import json
import os
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
import glob

class DataLoader:
    """
    Loads data from TechnicalAnalysis, FundamentalData, SentimentData, and AlternativeData folders
    """
    
    def __init__(self):
        # Get the project root directory
        self.root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Define data folders - Data is in IBM subfolder
        self.folders = {
            'technical': os.path.join(self.root_dir, 'IBM', 'TechnicalAnalysis'),
            'fundamental': os.path.join(self.root_dir, 'IBM', 'FundamentalData'),
            'sentiment': os.path.join(self.root_dir, 'IBM', 'SentimentData'),
            'alternative': os.path.join(self.root_dir, 'IBM', 'AlternativeData')
        }
        
        # Cache for loaded data
        self.cache = {}
    
    def get_available_symbols(self) -> List[str]:
        """
        Get list of symbols that have data available
        Currently only IBM, but designed to support multiple
        """
        symbols = set()
        
        # Check each folder for available data
        for folder_type, folder_path in self.folders.items():
            if os.path.exists(folder_path):
                # Look for JSON files
                files = glob.glob(os.path.join(folder_path, '**/*.json'), recursive=True)
                for file in files:
                    # Extract symbol from filename (assumes format like ibm_*.json)
                    filename = os.path.basename(file).lower()
                    if 'ibm' in filename:
                        symbols.add('IBM')
                    # Add logic for other symbols as needed
        
        return sorted(list(symbols))
    
    def load_price_data(self, symbol: str = 'IBM') -> pd.DataFrame:
        """
        Load price data for technical analysis
        Prioritizes daily data, falls back to weekly if needed
        """
        symbol_lower = symbol.lower()
        
        # Try to load from cache first
        cache_key = f"{symbol}_price"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Try daily data first - files are directly in technical folder
        technical_path = self.folders['technical']
        if os.path.exists(technical_path):
            # Look for daily adjusted data
            files = glob.glob(os.path.join(technical_path, f'{symbol_lower}_daily*.json'))
            if files:
                # Get the most recent file
                latest_file = max(files, key=os.path.getctime)
                data = self._load_json_file(latest_file)
                df = self._parse_price_data(data)
                if df is not None:
                    self.cache[cache_key] = df
                    return df
        
        # Fallback to weekly data
        if os.path.exists(technical_path):
            files = glob.glob(os.path.join(technical_path, f'{symbol_lower}_weekly*.json'))
            if files:
                latest_file = max(files, key=os.path.getctime)
                data = self._load_json_file(latest_file)
                df = self._parse_price_data(data)
                if df is not None:
                    self.cache[cache_key] = df
                    return df
        
        # If no data found, return empty DataFrame
        return pd.DataFrame()
    
    def _parse_price_data(self, data: Dict) -> pd.DataFrame:
        """
        Parse Alpha Vantage price data into DataFrame
        """
        if not data:
            return None
        
        # Find the time series key
        time_series_key = None
        for key in data.keys():
            if 'Time Series' in key or 'time series' in key.lower():
                time_series_key = key
                break
        
        if not time_series_key:
            return None
        
        time_series = data.get(time_series_key, {})
        
        # Convert to DataFrame
        rows = []
        for date, values in time_series.items():
            row = {
                'date': date,
                'open': float(values.get('1. open', values.get('open', 0))),
                'high': float(values.get('2. high', values.get('high', 0))),
                'low': float(values.get('3. low', values.get('low', 0))),
                'close': float(values.get('4. close', values.get('close', 0))),
                'volume': int(values.get('6. volume', values.get('5. volume', values.get('volume', 0))))
            }
            
            # Handle adjusted close if available
            if '5. adjusted close' in values or 'adjusted_close' in values:
                row['adjusted_close'] = float(values.get('5. adjusted close', values.get('adjusted_close', 0)))
            
            rows.append(row)
        
        if not rows:
            return None
        
        df = pd.DataFrame(rows)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        
        return df
    
    def load_fundamental_data(self, symbol: str = 'IBM') -> Dict:
        """
        Load fundamental data (company overview, financials)
        """
        symbol_lower = symbol.lower()
        
        # Try to load from cache
        cache_key = f"{symbol}_fundamental"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = {}
        
        # Load company overview
        overview_files = glob.glob(
            os.path.join(self.folders['fundamental'], 'company_overview*.json')
        )
        if overview_files:
            latest_file = max(overview_files, key=os.path.getctime)
            result['overview'] = self._load_json_file(latest_file)
        
        # Load income statement
        income_files = glob.glob(
            os.path.join(self.folders['fundamental'], 'income_statement*.json')
        )
        if income_files:
            latest_file = max(income_files, key=os.path.getctime)
            result['income'] = self._load_json_file(latest_file)
        
        # Load balance sheet
        balance_files = glob.glob(
            os.path.join(self.folders['fundamental'], 'balance_sheet*.json')
        )
        if balance_files:
            latest_file = max(balance_files, key=os.path.getctime)
            result['balance'] = self._load_json_file(latest_file)
        
        # Load cash flow
        cash_files = glob.glob(
            os.path.join(self.folders['fundamental'], 'cash_flow*.json')
        )
        if cash_files:
            latest_file = max(cash_files, key=os.path.getctime)
            result['cash_flow'] = self._load_json_file(latest_file)
        
        # Load earnings
        earnings_files = glob.glob(
            os.path.join(self.folders['fundamental'], 'earnings_history*.json')
        )
        if earnings_files:
            latest_file = max(earnings_files, key=os.path.getctime)
            result['earnings'] = self._load_json_file(latest_file)
        
        self.cache[cache_key] = result
        return result
    
    def load_sentiment_data(self, symbol: str = 'IBM') -> Dict:
        """
        Load sentiment data (news, earnings transcripts, sentiment scores)
        """
        symbol_lower = symbol.lower()
        
        # Try to load from cache
        cache_key = f"{symbol}_sentiment"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        result = {}
        
        # Load earnings transcripts
        transcript_files = glob.glob(
            os.path.join(self.folders['sentiment'], 'earnings_transcript_*.json')
        )
        if transcript_files:
            transcripts = []
            for file in transcript_files:
                data = self._load_json_file(file)
                if data:
                    transcripts.append(data)
            result['transcripts'] = transcripts
        
        # Load financial news (if EODHD data exists)
        news_files = glob.glob(
            os.path.join(self.folders['sentiment'], 'financial_news*.json')
        )
        if news_files:
            latest_file = max(news_files, key=os.path.getctime)
            result['news'] = self._load_json_file(latest_file)
        
        # Load sentiment scores (if EODHD data exists)
        sentiment_files = glob.glob(
            os.path.join(self.folders['sentiment'], 'sentiment_scores*.json')
        )
        if sentiment_files:
            latest_file = max(sentiment_files, key=os.path.getctime)
            result['scores'] = self._load_json_file(latest_file)
        
        self.cache[cache_key] = result
        return result
    
    def load_insider_data(self, symbol: str = 'IBM') -> Dict:
        """
        Load insider trading data
        """
        symbol_lower = symbol.lower()
        
        # Try to load from cache
        cache_key = f"{symbol}_insider"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Load insider transactions
        insider_files = glob.glob(
            os.path.join(self.folders['alternative'], 'insider_transactions*.json')
        )
        
        if insider_files:
            latest_file = max(insider_files, key=os.path.getctime)
            data = self._load_json_file(latest_file)
            
            # Process insider data
            if data and 'data' in data:
                transactions = data['data']
                
                # Calculate summary metrics
                buy_count = 0
                sell_count = 0
                buy_value = 0
                sell_value = 0
                
                for trans in transactions:
                    trans_type = trans.get('transaction_type', '').lower()
                    shares = float(trans.get('securities_transacted', 0))
                    price = float(trans.get('security_price', 0))
                    value = shares * price
                    
                    if 'buy' in trans_type or 'acquisition' in trans_type:
                        buy_count += 1
                        buy_value += value
                    elif 'sell' in trans_type or 'sale' in trans_type:
                        sell_count += 1
                        sell_value += value
                
                result = {
                    'transactions': transactions[:50],  # Latest 50 transactions
                    'buyers': buy_count,
                    'sellers': sell_count,
                    'buy_value': buy_value,
                    'sell_value': sell_value,
                    'net_value': buy_value - sell_value,
                    'recent_activity': self._analyze_insider_clusters(transactions[:10])
                }
                
                self.cache[cache_key] = result
                return result
        
        return {}
    
    def _analyze_insider_clusters(self, recent_transactions: List) -> str:
        """Analyze recent insider transactions for clusters"""
        if not recent_transactions:
            return 'none'
        
        buy_count = sum(1 for t in recent_transactions 
                       if 'buy' in t.get('transaction_type', '').lower() 
                       or 'acquisition' in t.get('transaction_type', '').lower())
        sell_count = sum(1 for t in recent_transactions 
                        if 'sell' in t.get('transaction_type', '').lower() 
                        or 'sale' in t.get('transaction_type', '').lower())
        
        if buy_count >= 5:
            return 'buying_cluster'
        elif sell_count >= 5:
            return 'selling_cluster'
        elif buy_count > sell_count:
            return 'moderate_buying'
        elif sell_count > buy_count:
            return 'moderate_selling'
        else:
            return 'mixed'
    
    def load_company_overview(self, symbol: str = 'IBM') -> Dict:
        """
        Load company overview data
        """
        fundamental = self.load_fundamental_data(symbol)
        return fundamental.get('overview', {})
    
    def _load_json_file(self, filepath: str) -> Dict:
        """
        Load JSON file and handle errors
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {str(e)}")
            return {}
    
    def fetch_data_for_symbol(self, symbol: str) -> Dict:
        """
        Fetch fresh data for a new symbol using the existing fetch scripts
        This would trigger the API calls we set up earlier
        """
        # This is a placeholder for triggering data fetching
        # In production, this would call the actual API fetching scripts
        
        return {
            'success': False,
            'error': f"Data fetching for new symbols not implemented yet. Only IBM data is available.",
            'data_types': []
        }
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache = {}
