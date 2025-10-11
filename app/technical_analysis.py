"""
Technical Analysis Module
Implements standard technical indicators and analysis
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple
import json
from datetime import datetime, timedelta

class TechnicalAnalyzer:
    """
    Comprehensive technical analysis calculator
    """
    
    def __init__(self):
        self.indicators = {}
        
    def calculate_all_indicators(self, price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate all technical indicators for given price data
        
        Returns comprehensive technical analysis including:
        - Moving Averages (SMA, EMA)
        - RSI (Relative Strength Index)
        - MACD (Moving Average Convergence Divergence)
        - Bollinger Bands
        - Volume Analysis
        - Support/Resistance Levels
        - Trend Analysis
        """
        
        # Ensure we have the required columns
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        
        # Calculate individual indicators
        sma_data = self.calculate_sma(price_data)
        ema_data = self.calculate_ema(price_data)
        rsi = self.calculate_rsi(price_data)
        macd = self.calculate_macd(price_data)
        bollinger = self.calculate_bollinger_bands(price_data)
        volume_analysis = self.analyze_volume(price_data)
        support_resistance = self.calculate_support_resistance(price_data)
        trend = self.identify_trend(price_data, sma_data)
        stochastic = self.calculate_stochastic(price_data)
        atr = self.calculate_atr(price_data)
        
        # Get current price info
        latest_price = float(price_data['close'].iloc[-1])
        prev_close = float(price_data['close'].iloc[-2])
        price_change = latest_price - prev_close
        price_change_percent = (price_change / prev_close) * 100
        
        # Calculate signal strength
        signal_strength = self.calculate_signal_strength({
            'rsi': rsi,
            'macd': macd,
            'sma': sma_data,
            'volume': volume_analysis,
            'price': latest_price
        })
        
        return {
            'current_price': latest_price,
            'price_change': round(price_change, 2),
            'price_change_percent': round(price_change_percent, 2),
            'volume': int(price_data['volume'].iloc[-1]),
            'sma': sma_data,
            'ema': ema_data,
            'rsi': rsi,
            'macd': macd,
            'bollinger_bands': bollinger,
            'volume_analysis': volume_analysis,
            'support_resistance': support_resistance,
            'trend': trend,
            'stochastic': stochastic,
            'atr': atr,
            'signal_strength': signal_strength,
            'volatility': self.calculate_volatility(price_data)
        }
    
    def calculate_sma(self, df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict[str, float]:
        """Calculate Simple Moving Averages"""
        sma_values = {}
        for period in periods:
            if len(df) >= period:
                sma = df['close'].rolling(window=period).mean().iloc[-1]
                sma_values[f'sma_{period}'] = round(float(sma), 2)
            else:
                sma_values[f'sma_{period}'] = None
        return sma_values
    
    def calculate_ema(self, df: pd.DataFrame, periods: List[int] = [12, 26]) -> Dict[str, float]:
        """Calculate Exponential Moving Averages"""
        ema_values = {}
        for period in periods:
            if len(df) >= period:
                ema = df['close'].ewm(span=period, adjust=False).mean().iloc[-1]
                ema_values[f'ema_{period}'] = round(float(ema), 2)
            else:
                ema_values[f'ema_{period}'] = None
        return ema_values
    
    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Relative Strength Index
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        if len(df) < period:
            return 50.0  # Neutral
            
        close_prices = df['close'].values
        deltas = np.diff(close_prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(float(rsi), 2)
    
    def calculate_macd(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        MACD = 12-day EMA - 26-day EMA
        Signal = 9-day EMA of MACD
        Histogram = MACD - Signal
        """
        if len(df) < 26:
            return {'macd': 0, 'signal': 0, 'histogram': 0}
        
        # Calculate EMAs
        ema_12 = df['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df['close'].ewm(span=26, adjust=False).mean()
        
        # MACD line
        macd_line = ema_12 - ema_26
        
        # Signal line (9-day EMA of MACD)
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            'macd': round(float(macd_line.iloc[-1]), 3),
            'signal': round(float(signal_line.iloc[-1]), 3),
            'histogram': round(float(histogram.iloc[-1]), 3)
        }
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """
        Calculate Bollinger Bands
        Middle Band = SMA(20)
        Upper Band = SMA(20) + (2 * Standard Deviation)
        Lower Band = SMA(20) - (2 * Standard Deviation)
        """
        if len(df) < period:
            return {'upper': 0, 'middle': 0, 'lower': 0, 'width': 0}
        
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        band_width = upper_band - lower_band
        
        return {
            'upper': round(float(upper_band.iloc[-1]), 2),
            'middle': round(float(sma.iloc[-1]), 2),
            'lower': round(float(lower_band.iloc[-1]), 2),
            'width': round(float(band_width.iloc[-1]), 2),
            'percent_b': round(float((df['close'].iloc[-1] - lower_band.iloc[-1]) / band_width.iloc[-1]), 3)
        }
    
    def calculate_stochastic(self, df: pd.DataFrame, period: int = 14) -> Dict[str, float]:
        """
        Calculate Stochastic Oscillator
        %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
        %D = 3-day SMA of %K
        """
        if len(df) < period:
            return {'k': 50, 'd': 50}
        
        low_min = df['low'].rolling(window=period).min()
        high_max = df['high'].rolling(window=period).max()
        
        k_percent = 100 * ((df['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=3).mean()
        
        return {
            'k': round(float(k_percent.iloc[-1]), 2),
            'd': round(float(d_percent.iloc[-1]), 2)
        }
    
    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR) for volatility
        """
        if len(df) < period:
            return 0.0
        
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values
        
        tr1 = high - low
        tr2 = abs(high - np.roll(close, 1))
        tr3 = abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-period:])
        
        return round(float(atr), 2)
    
    def analyze_volume(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Comprehensive volume analysis
        """
        current_volume = int(df['volume'].iloc[-1])
        avg_volume_20 = int(df['volume'].rolling(window=20).mean().iloc[-1])
        avg_volume_50 = int(df['volume'].rolling(window=50).mean().iloc[-1]) if len(df) >= 50 else avg_volume_20
        
        volume_ratio = current_volume / avg_volume_20 if avg_volume_20 > 0 else 1
        
        # Volume trend
        recent_volumes = df['volume'].tail(5)
        volume_trend = "increasing" if recent_volumes.iloc[-1] > recent_volumes.mean() else "decreasing"
        
        # Price-Volume relationship
        price_change = df['close'].iloc[-1] - df['close'].iloc[-2]
        
        if price_change > 0 and volume_ratio > 1.2:
            signal = "bullish_strong"
            interpretation = "Price up on high volume - Strong bullish signal"
        elif price_change > 0 and volume_ratio < 0.8:
            signal = "bullish_weak"
            interpretation = "Price up on low volume - Weak bullish signal"
        elif price_change < 0 and volume_ratio > 1.2:
            signal = "bearish_strong"
            interpretation = "Price down on high volume - Strong bearish signal"
        elif price_change < 0 and volume_ratio < 0.8:
            signal = "bearish_weak"
            interpretation = "Price down on low volume - Weak bearish signal"
        else:
            signal = "neutral"
            interpretation = "Normal volume activity"
        
        return {
            'current': current_volume,
            'avg_20': avg_volume_20,
            'avg_50': avg_volume_50,
            'ratio': round(volume_ratio, 2),
            'trend': volume_trend,
            'signal': signal,
            'interpretation': interpretation
        }
    
    def calculate_support_resistance(self, df: pd.DataFrame, lookback: int = 20) -> Dict[str, List[float]]:
        """
        Calculate support and resistance levels using pivot points and recent highs/lows
        """
        if len(df) < lookback:
            return {'support': [], 'resistance': []}
        
        recent_data = df.tail(lookback)
        
        # Method 1: Recent highs and lows
        highs = recent_data['high'].values
        lows = recent_data['low'].values
        
        # Find local maxima and minima
        resistance_levels = []
        support_levels = []
        
        for i in range(1, len(highs) - 1):
            if highs[i] > highs[i-1] and highs[i] > highs[i+1]:
                resistance_levels.append(float(highs[i]))
            if lows[i] < lows[i-1] and lows[i] < lows[i+1]:
                support_levels.append(float(lows[i]))
        
        # Method 2: Pivot points
        last_high = float(df['high'].iloc[-1])
        last_low = float(df['low'].iloc[-1])
        last_close = float(df['close'].iloc[-1])
        
        pivot = (last_high + last_low + last_close) / 3
        r1 = (2 * pivot) - last_low
        r2 = pivot + (last_high - last_low)
        s1 = (2 * pivot) - last_high
        s2 = pivot - (last_high - last_low)
        
        # Combine and sort
        resistance_levels.extend([r1, r2])
        support_levels.extend([s1, s2])
        
        # Remove duplicates and sort
        resistance_levels = sorted(list(set([round(r, 2) for r in resistance_levels])))[-3:]
        support_levels = sorted(list(set([round(s, 2) for s in support_levels])), reverse=True)[:3]
        
        return {
            'support': support_levels,
            'resistance': resistance_levels,
            'pivot': round(pivot, 2)
        }
    
    def identify_trend(self, df: pd.DataFrame, sma_data: Dict[str, float]) -> str:
        """
        Identify current trend using multiple methods
        """
        current_price = float(df['close'].iloc[-1])
        
        # Method 1: SMA alignment
        sma_20 = sma_data.get('sma_20', current_price)
        sma_50 = sma_data.get('sma_50', current_price)
        sma_200 = sma_data.get('sma_200', current_price)
        
        # Method 2: Price action
        recent_prices = df['close'].tail(10)
        price_trend_up = recent_prices.iloc[-1] > recent_prices.iloc[0]
        
        # Method 3: Higher highs and higher lows
        recent_highs = df['high'].tail(10)
        recent_lows = df['low'].tail(10)
        
        higher_highs = recent_highs.iloc[-1] > recent_highs.iloc[0]
        higher_lows = recent_lows.iloc[-1] > recent_lows.iloc[0]
        
        # Determine trend
        bullish_signals = 0
        
        if sma_20 and current_price > sma_20:
            bullish_signals += 1
        if sma_50 and current_price > sma_50:
            bullish_signals += 1
        if sma_200 and current_price > sma_200:
            bullish_signals += 1
        if price_trend_up:
            bullish_signals += 1
        if higher_highs and higher_lows:
            bullish_signals += 2
        
        if bullish_signals >= 4:
            return "strong_uptrend"
        elif bullish_signals >= 2:
            return "uptrend"
        elif bullish_signals >= 1:
            return "neutral"
        else:
            return "downtrend"
    
    def calculate_volatility(self, df: pd.DataFrame, period: int = 20) -> float:
        """
        Calculate historical volatility (standard deviation of returns)
        """
        if len(df) < period:
            return 0.0
        
        returns = df['close'].pct_change().dropna()
        volatility = returns.tail(period).std() * np.sqrt(252)  # Annualized
        
        return round(float(volatility * 100), 2)  # As percentage
    
    def calculate_signal_strength(self, indicators: Dict) -> Dict[str, Any]:
        """
        Calculate overall signal strength based on all indicators
        Returns a value between -100 (strong sell) and +100 (strong buy)
        """
        signal_points = 0
        total_weight = 0
        signals = []
        
        # RSI Signal (weight: 20)
        rsi = indicators['rsi']
        if rsi > 70:
            signal_points -= 15
            signals.append("RSI overbought")
        elif rsi < 30:
            signal_points += 15
            signals.append("RSI oversold")
        elif 50 < rsi < 60:
            signal_points += 5
            signals.append("RSI bullish")
        elif 40 < rsi < 50:
            signal_points -= 5
            signals.append("RSI bearish")
        total_weight += 20
        
        # MACD Signal (weight: 25)
        macd = indicators['macd']
        if macd['histogram'] > 0:
            signal_points += 15
            if macd['macd'] > macd['signal']:
                signal_points += 10
                signals.append("MACD bullish crossover")
        else:
            signal_points -= 15
            if macd['macd'] < macd['signal']:
                signal_points -= 10
                signals.append("MACD bearish crossover")
        total_weight += 25
        
        # SMA Signal (weight: 20)
        sma = indicators['sma']
        price = indicators['price']
        if sma.get('sma_20') and sma.get('sma_50'):
            if price > sma['sma_20'] > sma['sma_50']:
                signal_points += 20
                signals.append("Price above moving averages")
            elif price < sma['sma_20'] < sma['sma_50']:
                signal_points -= 20
                signals.append("Price below moving averages")
        total_weight += 20
        
        # Volume Signal (weight: 15)
        volume = indicators['volume']
        if volume['signal'] == 'bullish_strong':
            signal_points += 15
            signals.append("Strong volume confirmation")
        elif volume['signal'] == 'bearish_strong':
            signal_points -= 15
            signals.append("Strong selling volume")
        total_weight += 15
        
        # Normalize to -100 to +100
        if total_weight > 0:
            signal_strength = (signal_points / total_weight) * 100
        else:
            signal_strength = 0
        
        # Determine action
        if signal_strength > 30:
            action = "STRONG BUY"
        elif signal_strength > 10:
            action = "BUY"
        elif signal_strength < -30:
            action = "STRONG SELL"
        elif signal_strength < -10:
            action = "SELL"
        else:
            action = "HOLD"
        
        return {
            'strength': round(signal_strength, 2),
            'action': action,
            'signals': signals,
            'confidence': min(100, abs(signal_strength) * 1.5)
        }
    
    def get_latest_price_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get latest price information"""
        if df.empty:
            return {
                'price': 0,
                'open': 0,
                'high': 0,
                'low': 0,
                'volume': 0,
                'timestamp': datetime.now()
            }
        
        return {
            'price': float(df['close'].iloc[-1]),
            'open': float(df['open'].iloc[-1]),
            'high': float(df['high'].iloc[-1]),
            'low': float(df['low'].iloc[-1]),
            'volume': int(df['volume'].iloc[-1]),
            'timestamp': df.index[-1] if hasattr(df.index, '__iter__') else datetime.now()
        }
    
    def prepare_chart_data(self, df: pd.DataFrame, limit: int = 100) -> Dict[str, List]:
        """
        Prepare data for charting
        """
        recent_data = df.tail(limit)
        
        # Convert dates to strings for JSON serialization
        dates = [str(d) for d in recent_data.index] if hasattr(recent_data.index, '__iter__') else [str(i) for i in range(len(recent_data))]
        
        # Convert to lists for JSON serialization
        chart_data = {
            'dates': dates,
            'prices': [float(x) for x in recent_data['close'].tolist()],
            'volumes': [int(x) for x in recent_data['volume'].tolist()],
            'high': [float(x) for x in recent_data['high'].tolist()],
            'low': [float(x) for x in recent_data['low'].tolist()],
            'open': [float(x) for x in recent_data['open'].tolist()]
        }
        
        # Add moving averages if available
        if len(df) >= 20:
            sma_20 = df['close'].rolling(window=20).mean().tail(limit)
            chart_data['sma_20'] = [float(x) if not pd.isna(x) else None for x in sma_20.tolist()]
        
        if len(df) >= 50:
            sma_50 = df['close'].rolling(window=50).mean().tail(limit)
            chart_data['sma_50'] = [float(x) if not pd.isna(x) else None for x in sma_50.tolist()]
        
        return chart_data
