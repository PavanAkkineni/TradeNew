"""
Trade Signal Generator Module
Combines multiple analysis types to generate comprehensive trade signals
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

class SignalGenerator:
    """
    Generate comprehensive trade signals based on multiple data sources
    """
    
    def __init__(self):
        # Weights for different analysis types
        self.weights = {
            'technical': 0.40,  # 40% weight
            'fundamental': 0.30,  # 30% weight
            'sentiment': 0.20,  # 20% weight
            'insider': 0.10  # 10% weight
        }
    
    def generate_signal(
        self, 
        technical: Dict[str, Any],
        fundamental: Optional[Dict[str, Any]] = None,
        sentiment: Optional[Dict[str, Any]] = None,
        insider: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive trade signal
        
        Returns:
        - signal: BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
        - strength: -100 to +100
        - confidence: 0 to 100%
        - reasoning: List of reasons
        - risk_level: LOW, MEDIUM, HIGH
        - entry/exit points
        """
        
        # Collect individual signals
        signals = []
        total_score = 0
        total_weight = 0
        reasoning = []
        
        # Technical Analysis Signal
        if technical:
            tech_signal = self._analyze_technical(technical)
            signals.append(tech_signal)
            total_score += tech_signal['score'] * self.weights['technical']
            total_weight += self.weights['technical']
            reasoning.extend(tech_signal['reasons'])
        
        # Fundamental Analysis Signal
        if fundamental:
            fund_signal = self._analyze_fundamental(fundamental)
            signals.append(fund_signal)
            total_score += fund_signal['score'] * self.weights['fundamental']
            total_weight += self.weights['fundamental']
            reasoning.extend(fund_signal['reasons'])
        
        # Sentiment Analysis Signal
        if sentiment:
            sent_signal = self._analyze_sentiment(sentiment)
            signals.append(sent_signal)
            total_score += sent_signal['score'] * self.weights['sentiment']
            total_weight += self.weights['sentiment']
            reasoning.extend(sent_signal['reasons'])
        
        # Insider Trading Signal
        if insider:
            insider_signal = self._analyze_insider(insider)
            signals.append(insider_signal)
            total_score += insider_signal['score'] * self.weights['insider']
            total_weight += self.weights['insider']
            reasoning.extend(insider_signal['reasons'])
        
        # Normalize final score
        if total_weight > 0:
            final_score = total_score / total_weight
        else:
            final_score = 0
        
        # Determine signal and risk
        signal, risk_level = self._determine_signal(final_score)
        
        # Calculate confidence based on agreement between signals
        confidence = self._calculate_confidence(signals)
        
        # Calculate entry/exit points
        entry_exit = self._calculate_entry_exit(technical, signal)
        
        return {
            'signal': signal,
            'strength': round(final_score, 2),
            'confidence': round(confidence, 2),
            'reasoning': reasoning[:10],  # Top 10 reasons
            'risk_level': risk_level,
            'entry_price': entry_exit['entry'],
            'stop_loss': entry_exit['stop_loss'],
            'take_profit': entry_exit['take_profit'],
            'timeframe': entry_exit['timeframe'],
            'timestamp': datetime.now().isoformat(),
            'components': {
                'technical': signals[0] if len(signals) > 0 else None,
                'fundamental': signals[1] if len(signals) > 1 else None,
                'sentiment': signals[2] if len(signals) > 2 else None,
                'insider': signals[3] if len(signals) > 3 else None
            }
        }
    
    def _analyze_technical(self, technical: Dict) -> Dict:
        """Analyze technical indicators"""
        score = 0
        reasons = []
        
        # RSI Analysis
        rsi = technical.get('rsi', 50)
        if rsi < 30:
            score += 30
            reasons.append(f"✅ RSI oversold at {rsi:.1f} (bullish)")
        elif rsi > 70:
            score -= 30
            reasons.append(f"⚠️ RSI overbought at {rsi:.1f} (bearish)")
        elif 50 < rsi < 60:
            score += 10
            reasons.append(f"📈 RSI trending bullish at {rsi:.1f}")
        
        # MACD Analysis
        macd = technical.get('macd', {})
        if macd.get('histogram', 0) > 0:
            score += 20
            reasons.append(f"✅ MACD histogram positive ({macd['histogram']:.3f})")
            if macd.get('macd', 0) > macd.get('signal', 0):
                score += 10
                reasons.append("✅ MACD above signal line (bullish crossover)")
        else:
            score -= 20
            reasons.append(f"⚠️ MACD histogram negative ({macd['histogram']:.3f})")
        
        # Moving Average Analysis
        sma = technical.get('sma', {})
        current_price = technical.get('current_price', 0)
        
        if sma.get('sma_20') and current_price > sma['sma_20']:
            score += 10
            reasons.append(f"📈 Price above SMA20 ({sma['sma_20']:.2f})")
        if sma.get('sma_50') and current_price > sma['sma_50']:
            score += 10
            reasons.append(f"📈 Price above SMA50 ({sma['sma_50']:.2f})")
        if sma.get('sma_200') and current_price > sma['sma_200']:
            score += 15
            reasons.append(f"✅ Price above SMA200 ({sma['sma_200']:.2f}) - Long-term bullish")
        
        # Bollinger Bands Analysis
        bollinger = technical.get('bollinger_bands', {})
        if bollinger.get('percent_b', 0.5) < 0.2:
            score += 20
            reasons.append("✅ Near lower Bollinger Band (oversold)")
        elif bollinger.get('percent_b', 0.5) > 0.8:
            score -= 20
            reasons.append("⚠️ Near upper Bollinger Band (overbought)")
        
        # Volume Analysis
        volume = technical.get('volume_analysis', {})
        if volume.get('signal') == 'bullish_strong':
            score += 15
            reasons.append("✅ Strong buying volume detected")
        elif volume.get('signal') == 'bearish_strong':
            score -= 15
            reasons.append("⚠️ Strong selling volume detected")
        
        # Trend Analysis
        trend = technical.get('trend', 'neutral')
        if 'uptrend' in trend:
            score += 15
            reasons.append(f"📈 {trend.replace('_', ' ').title()} detected")
        elif 'downtrend' in trend:
            score -= 15
            reasons.append(f"📉 {trend.replace('_', ' ').title()} detected")
        
        return {
            'score': max(-100, min(100, score)),
            'reasons': reasons,
            'type': 'technical'
        }
    
    def _analyze_fundamental(self, fundamental: Dict) -> Dict:
        """Analyze fundamental data"""
        score = 0
        reasons = []
        
        # P/E Ratio Analysis
        pe_ratio = fundamental.get('pe_ratio', 0)
        sector_avg_pe = fundamental.get('sector_avg_pe', 25)
        
        if 0 < pe_ratio < sector_avg_pe * 0.8:
            score += 30
            reasons.append(f"✅ Undervalued P/E: {pe_ratio:.2f} vs sector {sector_avg_pe:.2f}")
        elif pe_ratio > sector_avg_pe * 1.2:
            score -= 20
            reasons.append(f"⚠️ Overvalued P/E: {pe_ratio:.2f} vs sector {sector_avg_pe:.2f}")
        
        # Revenue Growth
        revenue_growth = fundamental.get('revenue_growth', 0)
        if revenue_growth > 10:
            score += 25
            reasons.append(f"✅ Strong revenue growth: {revenue_growth:.1f}%")
        elif revenue_growth < 0:
            score -= 25
            reasons.append(f"⚠️ Negative revenue growth: {revenue_growth:.1f}%")
        
        # Profit Margins
        profit_margin = fundamental.get('profit_margin', 0)
        if profit_margin > 15:
            score += 20
            reasons.append(f"✅ Healthy profit margin: {profit_margin:.1f}%")
        elif profit_margin < 5:
            score -= 15
            reasons.append(f"⚠️ Low profit margin: {profit_margin:.1f}%")
        
        # Debt to Equity
        debt_to_equity = fundamental.get('debt_to_equity', 0)
        if debt_to_equity < 0.5:
            score += 15
            reasons.append(f"✅ Low debt/equity: {debt_to_equity:.2f}")
        elif debt_to_equity > 2:
            score -= 20
            reasons.append(f"⚠️ High debt/equity: {debt_to_equity:.2f}")
        
        # ROE
        roe = fundamental.get('roe', 0)
        if roe > 15:
            score += 20
            reasons.append(f"✅ Strong ROE: {roe:.1f}%")
        elif roe < 5:
            score -= 15
            reasons.append(f"⚠️ Low ROE: {roe:.1f}%")
        
        return {
            'score': max(-100, min(100, score)),
            'reasons': reasons,
            'type': 'fundamental'
        }
    
    def _analyze_sentiment(self, sentiment: Dict) -> Dict:
        """Analyze sentiment data"""
        score = 0
        reasons = []
        
        # Overall sentiment score
        sentiment_score = sentiment.get('score', 0)  # -1 to 1
        normalized_score = sentiment_score * 50  # -50 to 50
        score += normalized_score
        
        if sentiment_score > 0.5:
            reasons.append(f"✅ Very positive sentiment: {sentiment_score:.2f}")
        elif sentiment_score > 0.2:
            reasons.append(f"📈 Positive sentiment: {sentiment_score:.2f}")
        elif sentiment_score < -0.5:
            reasons.append(f"⚠️ Very negative sentiment: {sentiment_score:.2f}")
        elif sentiment_score < -0.2:
            reasons.append(f"📉 Negative sentiment: {sentiment_score:.2f}")
        
        # News volume
        news_volume = sentiment.get('news_volume', 0)
        if news_volume > 100:
            score += 10
            reasons.append(f"📰 High news coverage: {news_volume} articles")
        
        # Sentiment trend
        trend = sentiment.get('trend', 'neutral')
        if trend == 'improving':
            score += 20
            reasons.append("✅ Sentiment trend improving")
        elif trend == 'deteriorating':
            score -= 20
            reasons.append("⚠️ Sentiment trend deteriorating")
        
        # Social media buzz
        social_buzz = sentiment.get('social_buzz', 0)
        if social_buzz > 80:
            score += 15
            reasons.append(f"🔥 High social media buzz: {social_buzz}%")
        
        return {
            'score': max(-100, min(100, score)),
            'reasons': reasons,
            'type': 'sentiment'
        }
    
    def _analyze_insider(self, insider: Dict) -> Dict:
        """Analyze insider trading data"""
        score = 0
        reasons = []
        
        # Net insider buying/selling
        net_transactions = insider.get('net_value', 0)
        
        if net_transactions > 1000000:
            score += 50
            reasons.append(f"✅ Strong insider buying: ${net_transactions/1e6:.2f}M")
        elif net_transactions > 100000:
            score += 25
            reasons.append(f"📈 Insider buying: ${net_transactions/1e3:.0f}K")
        elif net_transactions < -1000000:
            score -= 40
            reasons.append(f"⚠️ Heavy insider selling: ${abs(net_transactions)/1e6:.2f}M")
        elif net_transactions < -100000:
            score -= 20
            reasons.append(f"📉 Insider selling: ${abs(net_transactions)/1e3:.0f}K")
        
        # Number of buyers vs sellers
        buyers = insider.get('buyers', 0)
        sellers = insider.get('sellers', 0)
        
        if buyers > sellers * 2:
            score += 25
            reasons.append(f"✅ More insiders buying: {buyers} vs {sellers}")
        elif sellers > buyers * 2:
            score -= 25
            reasons.append(f"⚠️ More insiders selling: {sellers} vs {buyers}")
        
        # Recent activity
        recent_activity = insider.get('recent_activity', 'none')
        if recent_activity == 'buying_cluster':
            score += 25
            reasons.append("✅ Cluster of insider buying detected")
        elif recent_activity == 'selling_cluster':
            score -= 25
            reasons.append("⚠️ Cluster of insider selling detected")
        
        return {
            'score': max(-100, min(100, score)),
            'reasons': reasons,
            'type': 'insider'
        }
    
    def _determine_signal(self, score: float) -> tuple:
        """Determine final signal and risk level based on score"""
        
        if score >= 50:
            return "STRONG BUY", "MEDIUM"
        elif score >= 25:
            return "BUY", "LOW"
        elif score >= 10:
            return "WEAK BUY", "LOW"
        elif score <= -50:
            return "STRONG SELL", "HIGH"
        elif score <= -25:
            return "SELL", "MEDIUM"
        elif score <= -10:
            return "WEAK SELL", "LOW"
        else:
            return "HOLD", "LOW"
    
    def _calculate_confidence(self, signals: List[Dict]) -> float:
        """Calculate confidence based on agreement between signals"""
        
        if not signals:
            return 0
        
        # Check agreement between signals
        scores = [s['score'] for s in signals]
        
        # All positive or all negative = high confidence
        all_positive = all(s > 0 for s in scores)
        all_negative = all(s < 0 for s in scores)
        
        if all_positive or all_negative:
            # Calculate average magnitude
            avg_magnitude = sum(abs(s) for s in scores) / len(scores)
            confidence = min(100, 50 + avg_magnitude * 0.5)
        else:
            # Mixed signals = lower confidence
            # Calculate standard deviation
            import numpy as np
            std_dev = np.std(scores)
            confidence = max(0, 50 - std_dev)
        
        return confidence
    
    def _calculate_entry_exit(self, technical: Dict, signal: str) -> Dict:
        """Calculate entry, stop loss, and take profit levels"""
        
        current_price = technical.get('current_price', 0)
        atr = technical.get('atr', current_price * 0.02)  # 2% default
        support_resistance = technical.get('support_resistance', {})
        
        if 'BUY' in signal:
            # Entry at current or slight pullback
            entry = current_price * 0.995  # Enter on 0.5% pullback
            
            # Stop loss below support or 2 ATR
            support_levels = support_resistance.get('support', [])
            if support_levels:
                stop_loss = min(support_levels[0] * 0.98, current_price - (2 * atr))
            else:
                stop_loss = current_price - (2 * atr)
            
            # Take profit at resistance levels or risk/reward ratios
            resistance_levels = support_resistance.get('resistance', [])
            if resistance_levels:
                take_profit = [
                    min(resistance_levels[0], current_price + (1.5 * atr)),  # TP1: 1.5x risk
                    current_price + (3 * atr),  # TP2: 3x risk
                    current_price + (5 * atr)   # TP3: 5x risk
                ]
            else:
                take_profit = [
                    current_price + (1.5 * atr),
                    current_price + (3 * atr),
                    current_price + (5 * atr)
                ]
            
            timeframe = "2-5 days" if 'STRONG' in signal else "5-10 days"
            
        elif 'SELL' in signal:
            # Entry at current or slight bounce
            entry = current_price * 1.005  # Enter on 0.5% bounce
            
            # Stop loss above resistance or 2 ATR
            resistance_levels = support_resistance.get('resistance', [])
            if resistance_levels:
                stop_loss = max(resistance_levels[-1] * 1.02, current_price + (2 * atr))
            else:
                stop_loss = current_price + (2 * atr)
            
            # Take profit at support levels
            support_levels = support_resistance.get('support', [])
            if support_levels:
                take_profit = [
                    max(support_levels[-1], current_price - (1.5 * atr)),
                    current_price - (3 * atr),
                    current_price - (5 * atr)
                ]
            else:
                take_profit = [
                    current_price - (1.5 * atr),
                    current_price - (3 * atr),
                    current_price - (5 * atr)
                ]
            
            timeframe = "2-5 days" if 'STRONG' in signal else "5-10 days"
            
        else:  # HOLD
            entry = current_price
            stop_loss = current_price * 0.95
            take_profit = [current_price * 1.05]
            timeframe = "Wait for better setup"
        
        return {
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit': [round(tp, 2) for tp in take_profit],
            'timeframe': timeframe,
            'risk_reward': round((take_profit[0] - entry) / (entry - stop_loss), 2) if entry != stop_loss else 0
        }
