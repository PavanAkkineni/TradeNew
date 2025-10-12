"""
Trading Signal Backtesting Script
==================================
Tests the credibility of trade signals from Sept 3 to Oct 3, 2024
Starting capital: $1000
Strategy: Follow trade signals generated each day using only data available up to that date

This script is completely separate from the website and only analyzes performance.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

SYMBOL = "IBM"
START_DATE = "2025-09-03"  # Updated to match available data
END_DATE = "2025-10-10"    # Updated to match available data
INITIAL_CAPITAL = 1000.0
DATA_FOLDER = Path(__file__).parent / "IBM"
PRICE_DATA_FILE = DATA_FOLDER / "TechnicalAnalysis" / "ibm_daily_adjusted_20251003_181415.json"
FUNDAMENTAL_FILE = DATA_FOLDER / "FundamentalData" / "company_overview_20251003_182715.json"
SENTIMENT_FILE = DATA_FOLDER / "SentimentData" / "sentiment_scores_20251003_185813.json"

# ============================================================================
# TECHNICAL INDICATORS CALCULATION
# ============================================================================

def calculate_rsi(prices, period=14):
    """Calculate RSI indicator"""
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """Calculate Bollinger Bands"""
    sma = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    return upper_band, sma, lower_band

def calculate_moving_averages(prices):
    """Calculate multiple moving averages"""
    sma_20 = prices.rolling(window=20).mean()
    sma_50 = prices.rolling(window=50).mean()
    sma_200 = prices.rolling(window=200).mean()
    return sma_20, sma_50, sma_200

# ============================================================================
# SIGNAL GENERATION LOGIC (Same as website)
# ============================================================================

def generate_technical_signal(data_up_to_date):
    """
    Generate technical analysis signal using only data up to specified date
    Returns: (score, signal_type, reasons)
    """
    df = data_up_to_date.copy()
    
    if len(df) < 50:  # Need minimum 50 days for most indicators
        return 0, "NEUTRAL", ["Insufficient historical data (need at least 50 days)"]
    
    close_prices = df['Close']
    volume = df['Volume']
    
    # Calculate indicators
    rsi = calculate_rsi(close_prices)
    macd_line, signal_line, histogram = calculate_macd(close_prices)
    upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(close_prices)
    sma_20, sma_50, sma_200 = calculate_moving_averages(close_prices)
    
    # Get latest values
    current_price = close_prices.iloc[-1]
    current_rsi = rsi.iloc[-1]
    current_macd = macd_line.iloc[-1]
    current_signal = signal_line.iloc[-1]
    current_histogram = histogram.iloc[-1]
    current_volume = volume.iloc[-1]
    avg_volume = volume.rolling(window=20).mean().iloc[-1]
    
    score = 0
    reasons = []
    
    # RSI Analysis (max ±15 points)
    if current_rsi < 30:
        score += 15
        reasons.append(f"✅ RSI Oversold ({current_rsi:.1f}) - Strong buy signal")
    elif current_rsi < 40:
        score += 10
        reasons.append(f"✅ RSI Low ({current_rsi:.1f}) - Bullish")
    elif current_rsi > 70:
        score -= 15
        reasons.append(f"⚠️ RSI Overbought ({current_rsi:.1f}) - Strong sell signal")
    elif current_rsi > 60:
        score -= 10
        reasons.append(f"⚠️ RSI High ({current_rsi:.1f}) - Bearish")
    else:
        reasons.append(f"➖ RSI Neutral ({current_rsi:.1f})")
    
    # MACD Analysis (max ±15 points)
    if current_macd > current_signal and current_histogram > 0:
        score += 15
        reasons.append(f"✅ MACD Bullish Crossover - Strong momentum")
    elif current_macd < current_signal and current_histogram < 0:
        score -= 15
        reasons.append(f"⚠️ MACD Bearish Crossover - Weak momentum")
    else:
        reasons.append(f"➖ MACD Neutral")
    
    # Moving Average Analysis (max ±20 points)
    if not pd.isna(sma_20.iloc[-1]) and not pd.isna(sma_50.iloc[-1]):
        # Check if we have 200 SMA (requires 200 days of data)
        if not pd.isna(sma_200.iloc[-1]):
            if sma_20.iloc[-1] > sma_50.iloc[-1] > sma_200.iloc[-1]:
                score += 20
                reasons.append(f"✅ Golden Cross Pattern - Strong uptrend")
            elif sma_20.iloc[-1] < sma_50.iloc[-1] < sma_200.iloc[-1]:
                score -= 20
                reasons.append(f"⚠️ Death Cross Pattern - Strong downtrend")
            elif current_price > sma_200.iloc[-1]:
                score += 10
                reasons.append(f"✅ Price above 200 SMA - Bullish trend")
            elif current_price < sma_200.iloc[-1]:
                score -= 10
                reasons.append(f"⚠️ Price below 200 SMA - Bearish trend")
        else:
            # No 200 SMA yet, just use 20 vs 50
            if sma_20.iloc[-1] > sma_50.iloc[-1]:
                score += 10
                reasons.append(f"✅ 20 SMA above 50 SMA - Bullish trend")
            elif sma_20.iloc[-1] < sma_50.iloc[-1]:
                score -= 10
                reasons.append(f"⚠️ 20 SMA below 50 SMA - Bearish trend")
    
    # Bollinger Bands (max ±10 points)
    if not pd.isna(lower_bb.iloc[-1]):
        if current_price < lower_bb.iloc[-1]:
            score += 10
            reasons.append(f"✅ Price below lower Bollinger Band - Oversold")
        elif current_price > upper_bb.iloc[-1]:
            score -= 10
            reasons.append(f"⚠️ Price above upper Bollinger Band - Overbought")
    
    # Volume Analysis (max ±5 points)
    if current_volume > avg_volume * 1.5:
        if score > 0:
            score += 5
            reasons.append(f"✅ High volume confirms bullish momentum")
        else:
            score -= 5
            reasons.append(f"⚠️ High volume confirms bearish momentum")
    
    # Determine signal type
    if score >= 25:
        signal_type = "STRONG_BUY"
    elif score >= 10:
        signal_type = "BUY"
    elif score >= 5:
        signal_type = "WEAK_BUY"
    elif score <= -25:
        signal_type = "STRONG_SELL"
    elif score <= -10:
        signal_type = "SELL"
    elif score <= -5:
        signal_type = "WEAK_SELL"
    else:
        signal_type = "HOLD"
    
    return score, signal_type, reasons

def generate_fundamental_signal(current_price):
    """
    Generate fundamental signal (using static data since we're using pre-generated IBM data)
    Returns: (score, reasons)
    """
    # Load fundamental data
    if not FUNDAMENTAL_FILE.exists():
        return 0, ["No fundamental data available"]
    
    try:
        with open(FUNDAMENTAL_FILE, 'r') as f:
            fund_data = json.load(f)
        
        score = 0
        reasons = []
        
        # P/E Ratio analysis (max ±8 points)
        pe_ratio_str = fund_data.get('PERatio', 'None')
        try:
            pe_ratio = float(pe_ratio_str) if pe_ratio_str != 'None' else 0
            if pe_ratio > 0:
                if pe_ratio < 15:
                    score += 8
                    reasons.append(f"✅ P/E Ratio ({pe_ratio:.1f}) - Undervalued")
                elif pe_ratio > 50:
                    score -= 8
                    reasons.append(f"⚠️ P/E Ratio ({pe_ratio:.1f}) - Severely overvalued")
                elif pe_ratio > 30:
                    score -= 3
                    reasons.append(f"⚠️ P/E Ratio ({pe_ratio:.1f}) - Overvalued")
                else:
                    reasons.append(f"➖ P/E Ratio ({pe_ratio:.1f}) - Fair value")
        except (ValueError, TypeError):
            pass
        
        # ROE analysis (max +8 points)
        roe_str = fund_data.get('ReturnOnEquityTTM', 'None')
        try:
            roe = float(roe_str) * 100 if roe_str != 'None' else 0
            if roe > 20:
                score += 8
                reasons.append(f"✅ ROE ({roe:.1f}%) - Excellent returns")
            elif roe > 15:
                score += 5
                reasons.append(f"✅ ROE ({roe:.1f}%) - Strong returns")
            elif roe > 10:
                score += 2
                reasons.append(f"➖ ROE ({roe:.1f}%) - Acceptable")
            elif roe > 0:
                reasons.append(f"➖ ROE ({roe:.1f}%) - Below average")
        except (ValueError, TypeError):
            pass
        
        # Profit margins (max +5 points)
        margin_str = fund_data.get('ProfitMargin', 'None')
        try:
            net_margin = float(margin_str) * 100 if margin_str != 'None' else 0
            if net_margin > 20:
                score += 5
                reasons.append(f"✅ Net Margin ({net_margin:.1f}%) - Excellent profitability")
            elif net_margin > 15:
                score += 3
                reasons.append(f"✅ Net Margin ({net_margin:.1f}%) - High profitability")
            elif net_margin > 10:
                score += 2
                reasons.append(f"➖ Net Margin ({net_margin:.1f}%) - Good profitability")
            elif net_margin > 0:
                reasons.append(f"➖ Net Margin ({net_margin:.1f}%) - Low margins")
        except (ValueError, TypeError):
            pass
        
        if not reasons:
            reasons.append("➖ Limited fundamental data available")
        
        return score, reasons
        
    except Exception as e:
        return 0, [f"⚠️ Error loading fundamentals: {str(e)}"]

def generate_sentiment_signal():
    """
    Generate sentiment signal (using static data)
    Returns: (score, reasons)
    """
    # Load sentiment data
    if not SENTIMENT_FILE.exists():
        return 0, ["No sentiment data available"]
    
    try:
        with open(SENTIMENT_FILE, 'r') as f:
            sent_data = json.load(f)
        
        score = 0
        reasons = []
        
        # Access the IBM.US sentiment data
        ibm_sentiments = sent_data.get('IBM.US', [])
        if ibm_sentiments:
            # Calculate average sentiment from recent data (last 5 days)
            recent_sentiments = [item['normalized'] for item in ibm_sentiments[:5]]
            overall_sentiment = sum(recent_sentiments) / len(recent_sentiments) if recent_sentiments else 0
        else:
            overall_sentiment = 0
        
        # Sentiment scoring (normalized values are typically 0-1 range, not -1 to 1)
        # Adjusted thresholds for 0-1 scale
        if overall_sentiment > 0.85:
            score += 10
            reasons.append(f"✅ Very positive market sentiment ({overall_sentiment:.2f})")
        elif overall_sentiment > 0.65:
            score += 5
            reasons.append(f"✅ Positive market sentiment ({overall_sentiment:.2f})")
        elif overall_sentiment < 0.35:
            score -= 10
            reasons.append(f"⚠️ Negative market sentiment ({overall_sentiment:.2f})")
        elif overall_sentiment < 0.50:
            score -= 5
            reasons.append(f"⚠️ Somewhat negative sentiment ({overall_sentiment:.2f})")
        else:
            reasons.append(f"➖ Neutral sentiment ({overall_sentiment:.2f})")
        
        return score, reasons
        
    except Exception as e:
        return 0, [f"⚠️ Error loading sentiment: {str(e)}"]

def generate_comprehensive_signal(data_up_to_date, current_price):
    """
    Generate comprehensive trade signal combining all factors
    Returns: dict with signal details
    """
    # Get component signals
    tech_score, tech_signal, tech_reasons = generate_technical_signal(data_up_to_date)
    fund_score, fund_reasons = generate_fundamental_signal(current_price)
    sent_score, sent_reasons = generate_sentiment_signal()
    
    # Calculate weighted total score
    # Technical: 100%, Fundamental: 70%, Sentiment: 60%
    total_score = tech_score + (fund_score * 0.7) + (sent_score * 0.6)
    
    # Determine final signal
    if total_score >= 35:
        final_signal = "STRONG_BUY"
        confidence = min(95, 60 + (total_score - 35))
        risk_level = "LOW"
    elif total_score >= 20:
        final_signal = "BUY"
        confidence = min(85, 55 + (total_score - 20))
        risk_level = "LOW"
    elif total_score >= 10:
        final_signal = "WEAK_BUY"
        confidence = min(75, 50 + (total_score - 10))
        risk_level = "MEDIUM"
    elif total_score <= -35:
        final_signal = "STRONG_SELL"
        confidence = min(95, 60 + abs(total_score + 35))
        risk_level = "HIGH"
    elif total_score <= -20:
        final_signal = "SELL"
        confidence = min(85, 55 + abs(total_score + 20))
        risk_level = "HIGH"
    elif total_score <= -10:
        final_signal = "WEAK_SELL"
        confidence = min(75, 50 + abs(total_score + 10))
        risk_level = "MEDIUM"
    else:
        final_signal = "HOLD"
        confidence = 40 + abs(total_score)
        risk_level = "MEDIUM"
    
    return {
        'signal': final_signal,
        'total_score': total_score,
        'confidence': confidence,
        'risk_level': risk_level,
        'technical_score': tech_score,
        'technical_signal': tech_signal,
        'fundamental_score': fund_score,
        'sentiment_score': sent_score,
        'reasons': {
            'technical': tech_reasons,
            'fundamental': fund_reasons,
            'sentiment': sent_reasons
        }
    }

# ============================================================================
# BACKTESTING ENGINE
# ============================================================================

def load_price_data():
    """Load IBM historical price data from JSON"""
    if not PRICE_DATA_FILE.exists():
        raise FileNotFoundError(f"Price data not found at {PRICE_DATA_FILE}")
    
    with open(PRICE_DATA_FILE, 'r') as f:
        data = json.load(f)
    
    # Extract time series data
    time_series = data.get('Time Series (Daily)', {})
    
    # Convert to DataFrame
    records = []
    for date_str, values in time_series.items():
        records.append({
            'Date': pd.to_datetime(date_str),
            'Open': float(values['1. open']),
            'High': float(values['2. high']),
            'Low': float(values['3. low']),
            'Close': float(values['4. close']),
            'Volume': int(values['6. volume'])  # Fixed: volume is key "6. volume"
        })
    
    df = pd.DataFrame(records)
    df = df.sort_values('Date').reset_index(drop=True)
    
    print(f"✅ Loaded {len(df)} days of price data")
    print(f"   Date range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    return df

def run_backtest():
    """
    Run backtest from START_DATE to END_DATE
    Generate signals for each day and track performance
    """
    print("=" * 80)
    print("TRADING SIGNAL BACKTEST")
    print("=" * 80)
    print(f"Symbol: {SYMBOL}")
    print(f"Period: {START_DATE} to {END_DATE}")
    print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"Strategy: Follow daily trade signals")
    print("=" * 80)
    print()
    
    # Load all data
    all_data = load_price_data()
    
    # Filter to our backtest period
    start_dt = pd.to_datetime(START_DATE)
    end_dt = pd.to_datetime(END_DATE)
    
    # Get all trading days in the period
    backtest_days = all_data[
        (all_data['Date'] >= start_dt) & 
        (all_data['Date'] <= end_dt)
    ].copy()
    
    if len(backtest_days) == 0:
        print("❌ No data available for the specified period")
        return
    
    print(f"📊 Found {len(backtest_days)} trading days in backtest period\n")
    
    # Initialize results storage
    results = []
    
    # Process each day
    for idx, row in backtest_days.iterrows():
        current_date = row['Date']
        current_price = row['Close']
        
        # Get data only up to current date (no look-ahead bias)
        data_up_to_date = all_data[all_data['Date'] <= current_date].copy()
        
        # Generate signal
        signal_data = generate_comprehensive_signal(data_up_to_date, current_price)
        
        # Store result
        result = {
            'date': current_date.strftime('%Y-%m-%d'),
            'price': current_price,
            'signal': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'risk_level': signal_data['risk_level'],
            'total_score': signal_data['total_score'],
            'technical_score': signal_data['technical_score'],
            'technical_signal': signal_data['technical_signal'],
            'fundamental_score': signal_data['fundamental_score'],
            'sentiment_score': signal_data['sentiment_score'],
            'reasons': signal_data['reasons']
        }
        results.append(result)
        
        # Print daily signal
        print(f"📅 {current_date.strftime('%Y-%m-%d')} | Price: ${current_price:.2f} | Signal: {signal_data['signal']} | Confidence: {signal_data['confidence']}% | Score: {signal_data['total_score']:.1f}")
        print(f"   Technical: {signal_data['technical_score']:.1f} | Fundamental: {signal_data['fundamental_score']:.1f} | Sentiment: {signal_data['sentiment_score']:.1f}")
        print()
    
    # Save results to JSON
    output_file = Path(__file__).parent / "backtest_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("=" * 80)
    print(f"✅ Backtest complete! Generated {len(results)} daily signals")
    print(f"📁 Results saved to: {output_file}")
    print("=" * 80)
    print()
    print("Next step: Run 'analyze_backtest_performance.py' to simulate trades and calculate returns")
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        results = run_backtest()
        
        # Print summary statistics
        if results:
            signals_count = {}
            for r in results:
                sig = r['signal']
                signals_count[sig] = signals_count.get(sig, 0) + 1
            
            print("\n📊 SIGNAL DISTRIBUTION:")
            print("-" * 40)
            for sig, count in sorted(signals_count.items()):
                pct = (count / len(results)) * 100
                print(f"  {sig:15s}: {count:3d} days ({pct:5.1f}%)")
            print()
            
    except Exception as e:
        print(f"❌ Error during backtest: {str(e)}")
        import traceback
        traceback.print_exc()
