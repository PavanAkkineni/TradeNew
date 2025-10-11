"""
Sentiment Analysis Module
Analyzes news, earnings transcripts, and social sentiment
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta

class SentimentAnalyzer:
    """
    Analyze sentiment from various sources:
    - Financial news
    - Earnings call transcripts
    - Sentiment scores
    """
    
    def __init__(self):
        self.sentiment_thresholds = {
            'very_positive': 0.5,
            'positive': 0.2,
            'neutral_high': 0.1,
            'neutral_low': -0.1,
            'negative': -0.2,
            'very_negative': -0.5
        }
    
    def analyze(self, sentiment_data: Dict) -> Dict[str, Any]:
        """
        Comprehensive sentiment analysis
        """
        if not sentiment_data:
            return {
                'score': 0,
                'trend': 'neutral',
                'news_volume': 0,
                'interpretation': 'No sentiment data available'
            }
        
        # Analyze different sentiment sources
        news_sentiment = self._analyze_news(sentiment_data.get('news', []))
        transcript_sentiment = self._analyze_transcripts(sentiment_data.get('transcripts', []))
        score_sentiment = self._analyze_scores(sentiment_data.get('scores', {}))
        
        # Combine sentiments with weights
        combined_score = 0
        total_weight = 0
        
        if news_sentiment:
            combined_score += news_sentiment['score'] * 0.35
            total_weight += 0.35
        
        if transcript_sentiment:
            combined_score += transcript_sentiment['score'] * 0.35
            total_weight += 0.35
        
        if score_sentiment:
            combined_score += score_sentiment['score'] * 0.30
            total_weight += 0.30
        
        # Normalize
        if total_weight > 0:
            final_score = combined_score / total_weight
        else:
            final_score = 0
        
        # Determine trend
        trend = self._determine_trend(score_sentiment.get('historical', []))
        
        # Calculate news volume and buzz
        news_volume = news_sentiment.get('article_count', 0)
        social_buzz = self._calculate_social_buzz(news_sentiment, score_sentiment)
        
        # Interpretation
        interpretation = self._interpret_sentiment(final_score, trend, news_volume)
        
        return {
            'score': round(final_score, 3),
            'trend': trend,
            'news_volume': news_volume,
            'social_buzz': social_buzz,
            'interpretation': interpretation,
            'components': {
                'news': news_sentiment,
                'transcripts': transcript_sentiment,
                'scores': score_sentiment
            },
            'signals': self._generate_sentiment_signals(final_score, trend, news_volume)
        }
    
    def _analyze_news(self, news_data: Any) -> Dict:
        """Analyze financial news sentiment"""
        if not news_data:
            return {'score': 0, 'article_count': 0}
        
        # Handle both list and dict formats
        if isinstance(news_data, dict):
            articles = news_data.get('articles', [])
        elif isinstance(news_data, list):
            articles = news_data
        else:
            return {'score': 0, 'article_count': 0}
        
        if not articles:
            return {'score': 0, 'article_count': 0}
        
        total_sentiment = 0
        count = 0
        positive_count = 0
        negative_count = 0
        
        for article in articles:
            sentiment = article.get('sentiment', {})
            if sentiment:
                # Polarity ranges from -1 to 1
                polarity = sentiment.get('polarity', 0)
                total_sentiment += polarity
                count += 1
                
                if polarity > 0.1:
                    positive_count += 1
                elif polarity < -0.1:
                    negative_count += 1
        
        avg_sentiment = total_sentiment / count if count > 0 else 0
        
        return {
            'score': avg_sentiment,
            'article_count': len(articles),
            'positive_articles': positive_count,
            'negative_articles': negative_count,
            'neutral_articles': count - positive_count - negative_count
        }
    
    def _analyze_transcripts(self, transcripts: List) -> Dict:
        """Analyze earnings call transcript sentiment"""
        if not transcripts:
            return {'score': 0, 'confidence': 0}
        
        total_sentiment = 0
        count = 0
        
        for transcript in transcripts:
            # Look for sentiment analysis in transcript
            sentiment_analysis = transcript.get('sentiment_analysis', {})
            if sentiment_analysis:
                overall = sentiment_analysis.get('overall_sentiment', 0)
                # Convert to -1 to 1 scale if necessary
                if isinstance(overall, str):
                    # Map text sentiment to numeric
                    sentiment_map = {
                        'very_positive': 0.8,
                        'positive': 0.5,
                        'neutral': 0,
                        'negative': -0.5,
                        'very_negative': -0.8
                    }
                    overall = sentiment_map.get(overall.lower(), 0)
                
                total_sentiment += overall
                count += 1
        
        avg_sentiment = total_sentiment / count if count > 0 else 0
        
        return {
            'score': avg_sentiment,
            'transcript_count': len(transcripts),
            'confidence': min(100, len(transcripts) * 12.5)  # More transcripts = higher confidence
        }
    
    def _analyze_scores(self, scores_data: Dict) -> Dict:
        """Analyze historical sentiment scores"""
        if not scores_data:
            return {'score': 0, 'historical': []}
        
        # Handle EODHD sentiment score format
        symbol_scores = None
        for key in scores_data:
            if key.endswith('.US') or 'IBM' in key:
                symbol_scores = scores_data[key]
                break
        
        if not symbol_scores:
            return {'score': 0, 'historical': []}
        
        # Calculate average recent sentiment
        recent_scores = symbol_scores[:10] if len(symbol_scores) > 10 else symbol_scores
        
        total = 0
        for score_data in recent_scores:
            normalized = score_data.get('normalized', 0)
            total += normalized
        
        avg_score = total / len(recent_scores) if recent_scores else 0
        
        return {
            'score': avg_score,
            'historical': symbol_scores,
            'data_points': len(symbol_scores)
        }
    
    def _determine_trend(self, historical_scores: List) -> str:
        """Determine sentiment trend from historical data"""
        if not historical_scores or len(historical_scores) < 5:
            return 'neutral'
        
        # Compare recent vs older sentiment
        recent = historical_scores[:5]
        older = historical_scores[10:15] if len(historical_scores) > 15 else historical_scores[-5:]
        
        recent_avg = sum(s.get('normalized', 0) for s in recent) / len(recent)
        older_avg = sum(s.get('normalized', 0) for s in older) / len(older)
        
        diff = recent_avg - older_avg
        
        if diff > 0.1:
            return 'improving'
        elif diff < -0.1:
            return 'deteriorating'
        else:
            return 'stable'
    
    def _calculate_social_buzz(self, news_sentiment: Dict, score_sentiment: Dict) -> float:
        """Calculate social media buzz metric (0-100)"""
        buzz = 50  # Base score
        
        # News volume impact
        article_count = news_sentiment.get('article_count', 0) if news_sentiment else 0
        if article_count > 50:
            buzz += 30
        elif article_count > 20:
            buzz += 15
        elif article_count < 5:
            buzz -= 20
        
        # Historical data points impact
        data_points = score_sentiment.get('data_points', 0) if score_sentiment else 0
        if data_points > 30:
            buzz += 20
        elif data_points > 10:
            buzz += 10
        
        return max(0, min(100, buzz))
    
    def _interpret_sentiment(self, score: float, trend: str, volume: int) -> str:
        """Generate human-readable sentiment interpretation"""
        
        # Determine sentiment level
        if score >= self.sentiment_thresholds['very_positive']:
            level = "Very positive"
        elif score >= self.sentiment_thresholds['positive']:
            level = "Positive"
        elif score >= self.sentiment_thresholds['neutral_high']:
            level = "Slightly positive"
        elif score >= self.sentiment_thresholds['neutral_low']:
            level = "Neutral"
        elif score >= self.sentiment_thresholds['negative']:
            level = "Negative"
        else:
            level = "Very negative"
        
        # Add trend context
        if trend == 'improving':
            trend_text = " and improving"
        elif trend == 'deteriorating':
            trend_text = " but deteriorating"
        else:
            trend_text = " and stable"
        
        # Add volume context
        if volume > 50:
            volume_text = " with high news coverage"
        elif volume > 20:
            volume_text = " with moderate news coverage"
        else:
            volume_text = " with low news coverage"
        
        return f"{level} sentiment{trend_text}{volume_text}"
    
    def _generate_sentiment_signals(self, score: float, trend: str, volume: int) -> List[str]:
        """Generate actionable signals from sentiment"""
        signals = []
        
        # Score-based signals
        if score >= self.sentiment_thresholds['very_positive']:
            signals.append("✅ Strong positive sentiment - Bullish signal")
        elif score >= self.sentiment_thresholds['positive']:
            signals.append("📈 Positive sentiment - Moderate bullish signal")
        elif score <= self.sentiment_thresholds['very_negative']:
            signals.append("🔴 Very negative sentiment - Bearish signal")
        elif score <= self.sentiment_thresholds['negative']:
            signals.append("📉 Negative sentiment - Moderate bearish signal")
        
        # Trend signals
        if trend == 'improving':
            signals.append("📈 Sentiment trend improving - Momentum building")
        elif trend == 'deteriorating':
            signals.append("📉 Sentiment trend deteriorating - Caution advised")
        
        # Volume signals
        if volume > 50:
            signals.append("🔥 High news volume - Increased volatility expected")
        elif volume < 5:
            signals.append("🔇 Low news coverage - Limited sentiment impact")
        
        return signals
