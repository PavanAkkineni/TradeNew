"""
Debug script to test data loading
"""
import sys
sys.path.insert(0, '.')

from app.data_loader import DataLoader
from app.technical_analysis import TechnicalAnalyzer

print("Testing data loading...")
print("="*60)

# Initialize loader
loader = DataLoader()
print(f"Data folders: {loader.folders}")

# Try to load price data
print("\nLoading IBM price data...")
price_data = loader.load_price_data('IBM')

print(f"Loaded data shape: {price_data.shape if not price_data.empty else 'EMPTY!'}")
print(f"Data columns: {price_data.columns.tolist() if not price_data.empty else 'N/A'}")
print(f"Date range: {price_data.index[0]} to {price_data.index[-1]}" if not price_data.empty else "No data")
print(f"Latest price: ${price_data['close'].iloc[-1]:.2f}" if not price_data.empty else "N/A")

if not price_data.empty:
    print("\nCalculating technical indicators...")
    analyzer = TechnicalAnalyzer()
    indicators = analyzer.calculate_all_indicators(price_data)
    
    print(f"Current price: ${indicators.get('current_price', 0):.2f}")
    print(f"RSI: {indicators.get('rsi', 0):.2f}")
    print(f"MACD: {indicators.get('macd', {})}")
    print(f"Trend: {indicators.get('trend', 'N/A')}")
else:
    print("\n❌ No data loaded! Check file paths.")
