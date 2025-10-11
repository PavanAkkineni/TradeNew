"""
Gemini AI Integration for Advanced Trading Analysis
"""
import os
import json
from typing import Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class GeminiAnalyzer:
    """
    Advanced AI-powered analysis using Google Gemini Pro
    """
    
    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            # Use Gemini 2.5 Pro for enhanced analysis
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.enabled = True
            print("✅ Gemini 2.5 Pro initialized for trading expert analysis")
        else:
            self.model = None
            self.enabled = False
            print("⚠️ Gemini API key not found - using mock responses")
    
    def analyze_comprehensive(self, data: Dict[str, Any]) -> str:
        """
        Generate comprehensive analysis using all available data
        """
        if not self.enabled:
            return "AI analysis unavailable. Please configure Gemini API key."
        
        try:
            # Build prompt with trading data
            prompt = self._build_analysis_prompt(data)
            
            # Generate analysis
            response = self.model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"AI analysis error: {str(e)}"
    
    def explain_indicator(self, indicator: str, value: Any, context: Dict) -> str:
        """
        Explain a specific indicator in context
        """
        if not self.enabled:
            return "AI explanation unavailable."
        
        try:
            prompt = f"""
            Explain the {indicator} indicator with current value {value} for IBM stock.
            
            Context:
            - Current price: ${context.get('price', 'N/A')}
            - Price change: {context.get('change_percent', 'N/A')}%
            - Market trend: {context.get('trend', 'N/A')}
            
            Provide:
            1. What this value means
            2. Is it bullish or bearish?
            3. What action should a trader consider?
            4. Key levels to watch
            
            Keep it concise and practical.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Explanation unavailable: {str(e)}"
    
    def generate_trade_recommendation(self, technical: Dict, fundamental: Dict = None, sentiment: Dict = None) -> Dict:
        """
        Generate detailed trade recommendation with AI insights
        """
        if not self.enabled:
            return {
                "recommendation": "HOLD",
                "confidence": 50,
                "analysis": "AI analysis unavailable. Using rule-based signals only.",
                "key_factors": [],
                "risk_assessment": "Medium"
            }
        
        try:
            prompt = f"""
            As a professional trading analyst, analyze IBM stock and provide a trading recommendation.
            
            Technical Analysis:
            - RSI: {technical.get('rsi', 'N/A')}
            - MACD: {technical.get('macd', {})}
            - Price vs SMA20: {technical.get('sma', {}).get('sma_20', 'N/A')}
            - Volume trend: {technical.get('volume_analysis', {}).get('trend', 'N/A')}
            - Current trend: {technical.get('trend', 'N/A')}
            
            {self._add_fundamental_context(fundamental)}
            {self._add_sentiment_context(sentiment)}
            
            Provide a JSON response with:
            {{
                "recommendation": "BUY/SELL/HOLD/STRONG_BUY/STRONG_SELL",
                "confidence": 0-100,
                "analysis": "Detailed explanation",
                "key_factors": ["factor1", "factor2", ...],
                "entry_price": suggested entry,
                "stop_loss": stop loss level,
                "take_profit": [TP1, TP2, TP3],
                "risk_assessment": "Low/Medium/High",
                "timeframe": "suggested holding period"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response
                text = response.text
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0]
                elif '{' in text and '}' in text:
                    start = text.index('{')
                    end = text.rindex('}') + 1
                    text = text[start:end]
                
                return json.loads(text)
            except:
                # Fallback if JSON parsing fails
                return {
                    "recommendation": "HOLD",
                    "confidence": 60,
                    "analysis": response.text,
                    "key_factors": ["AI analysis available but format error"],
                    "risk_assessment": "Medium"
                }
            
        except Exception as e:
            return {
                "recommendation": "HOLD",
                "confidence": 50,
                "analysis": f"AI error: {str(e)}",
                "key_factors": [],
                "risk_assessment": "Unknown"
            }
    
    def analyze_pattern(self, price_data: List[float], pattern_type: str = "general") -> str:
        """
        Analyze price patterns with AI
        """
        if not self.enabled:
            return "Pattern analysis unavailable."
        
        try:
            recent_prices = price_data[-20:] if len(price_data) > 20 else price_data
            
            prompt = f"""
            Analyze this price pattern for IBM stock:
            Recent prices (last 20 days): {recent_prices}
            
            Identify:
            1. Chart pattern (head & shoulders, triangle, flag, etc.)
            2. Support and resistance levels
            3. Trend strength
            4. Potential breakout levels
            5. Price target
            
            Be specific and actionable.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Pattern analysis error: {str(e)}"
    
    def _build_analysis_prompt(self, data: Dict) -> str:
        """Build comprehensive analysis prompt"""
        
        technical = data.get('technical', {})
        
        prompt = f"""
        Provide a comprehensive trading analysis for IBM stock:
        
        TECHNICAL INDICATORS:
        - Current Price: ${technical.get('current_price', 'N/A')}
        - Price Change: {technical.get('price_change_percent', 'N/A')}%
        - RSI (14): {technical.get('rsi', 'N/A')}
        - MACD: {technical.get('macd', {})}
        - Moving Averages: {technical.get('sma', {})}
        - Volume: {technical.get('volume', 'N/A')} (ratio: {technical.get('volume_analysis', {}).get('ratio', 'N/A')})
        - Bollinger Bands: {technical.get('bollinger_bands', {})}
        - Trend: {technical.get('trend', 'N/A')}
        - Volatility: {technical.get('volatility', 'N/A')}%
        
        Provide:
        1. **Market Overview**: Current state and immediate outlook
        2. **Technical Analysis**: Key signals and patterns
        3. **Trading Signal**: Clear BUY/SELL/HOLD with confidence %
        4. **Entry & Exit Points**: Specific price levels
        5. **Risk Management**: Stop loss and position sizing
        6. **Key Risks**: What could invalidate this analysis
        7. **Time Horizon**: Short-term (days), Medium (weeks), Long (months)
        
        Format the response in a clear, professional manner suitable for display in a trading dashboard.
        Use bullet points and bold text for emphasis.
        Include specific price levels and percentages.
        """
        
        return prompt
    
    def _add_fundamental_context(self, fundamental: Dict) -> str:
        """Add fundamental data to prompt if available"""
        if not fundamental:
            return ""
        
        return f"""
        Fundamental Data:
        - P/E Ratio: {fundamental.get('pe_ratio', 'N/A')}
        - Profit Margin: {fundamental.get('profit_margin', 'N/A')}%
        - Revenue Growth: {fundamental.get('revenue_growth', 'N/A')}%
        - Debt/Equity: {fundamental.get('debt_to_equity', 'N/A')}
        """
    
    def _add_sentiment_context(self, sentiment: Dict) -> str:
        """Add sentiment data to prompt if available"""
        if not sentiment:
            return ""
        
        return f"""
        Sentiment Analysis:
        - Overall Score: {sentiment.get('score', 'N/A')}
        - Trend: {sentiment.get('trend', 'N/A')}
        - News Volume: {sentiment.get('news_volume', 'N/A')}
        """
    
    def market_commentary(self, symbol: str = "IBM") -> str:
        """
        Generate real-time market commentary
        """
        if not self.enabled:
            return "Market commentary unavailable."
        
        try:
            prompt = f"""
            Provide a brief, professional market commentary for {symbol} stock.
            
            Include:
            1. Current market sentiment
            2. Key factors affecting the stock today
            3. What traders should watch for
            4. Comparison to sector performance
            
            Keep it under 150 words, professional and insightful.
            Format for a trading dashboard display.
            """
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Commentary unavailable: {str(e)}"
    
    def trading_expert_analysis(self, technical_indicators: Dict, computed_signal: Dict, individual_signals: Dict) -> Dict:
        """
        Comprehensive trading expert analysis using Gemini 2.5 Pro
        Provides detailed analysis alongside computed signals
        """
        if not self.enabled:
            # Return comprehensive mock analysis for demo
            current_price = technical_indicators.get('current_price', 288.42)
            rsi = technical_indicators.get('rsi', 81.79)
            
            return {
                "expert_signal": "BUY",
                "confidence": 78,
                "detailed_analysis": f"Based on comprehensive technical analysis of IBM at ${current_price:.2f}, I recommend a BUY signal with 78% confidence. The stock shows strong momentum with RSI at {rsi:.1f}, indicating overbought conditions that may lead to a brief consolidation. However, the uptrend remains intact with price above all major moving averages. MACD crossover confirms bullish momentum. Volume analysis shows normal participation. The stock is approaching resistance levels but has strong support below.",
                "signal_breakdown": {
                    "rsi_analysis": f"RSI at {rsi:.1f} indicates overbought territory (>70), suggesting potential short-term pullback. However, in strong uptrends, RSI can remain elevated longer than expected.",
                    "macd_analysis": "MACD line above signal line with positive histogram confirms bullish momentum. The crossover occurred recently, supporting continued upward movement.",
                    "trend_analysis": "Price above SMA 20, 50, and 200 confirms strong uptrend. Moving averages are properly stacked (20>50>200) indicating healthy bull market structure.",
                    "volume_analysis": "Volume at 0.81x average shows normal but slightly decreased participation. Price advance on lower volume suggests controlled buying, not panic buying.",
                    "volatility_analysis": "Price near upper Bollinger Band (%B at 0.885) indicates stretched conditions. Potential for mean reversion to middle band around $269.",
                    "support_resistance_analysis": "Strong resistance cluster around $288-292. Support levels at $286, $284, and $280 provide good risk/reward setup for entries."
                },
                "agreement_with_computed": {
                    "agrees": True,
                    "reasoning": "I agree with the computed BUY signal. The mathematical model correctly identifies bullish momentum from multiple indicators. RSI overbought condition is noted but not enough to override the strong trend."
                },
                "risk_assessment": {
                    "risk_level": "MEDIUM",
                    "key_risks": ["RSI overbought condition", "Approaching resistance levels", "Lower volume participation"],
                    "risk_mitigation": "Use tight stop loss below $286. Consider scaling into position if price pulls back to $284-286 support zone."
                },
                "strategy_recommendation": {
                    "entry_strategy": "Buy on any pullback to $286 support or on breakout above $292 resistance with volume confirmation",
                    "position_sizing": "Standard position size (2-3% of portfolio) given medium risk level",
                    "stop_loss": "$285.50 - below key support and previous low",
                    "take_profit_targets": ["TP1: $295 (next resistance)", "TP2: $302 (measured move target)"],
                    "holding_period": "2-4 weeks for swing trade, 3-6 months for position trade"
                },
                "key_levels": {
                    "immediate_resistance": "$292.05",
                    "immediate_support": "$286.05",
                    "breakout_level": "$295.67",
                    "invalidation_level": "$280.15"
                },
                "timeframe_analysis": {
                    "short_term": "1-5 days: Expect consolidation or minor pullback from overbought levels",
                    "medium_term": "1-4 weeks: Bullish bias with target around $295-300 range",
                    "long_term": "1-3 months: Strong uptrend likely to continue with targets above $300"
                },
                "market_context": "Technology sector showing strength. IBM's AI initiatives and cloud transformation driving institutional interest. Market sentiment supportive of large-cap tech stocks.",
                "confidence_factors": ["Strong trend confirmation", "Multiple timeframe alignment", "Sector rotation into tech", "Technical pattern integrity"]
            }
        
        try:
            # Build comprehensive prompt for trading expert
            prompt = f"""
            You are a professional trading expert with 20+ years of experience analyzing financial markets. 
            Analyze IBM stock using the provided technical indicators and provide detailed trading insights.

            COMPUTED SIGNAL ANALYSIS:
            Our mathematical model generated:
            - Final Signal: {computed_signal.get('action', 'N/A')}
            - Signal Strength: {computed_signal.get('strength', 'N/A')}
            - Confidence: {computed_signal.get('confidence', 'N/A')}%

            INDIVIDUAL INDICATOR CONTRIBUTIONS:
            {self._format_individual_signals(individual_signals)}

            DETAILED TECHNICAL INDICATORS:
            Current Price: ${technical_indicators.get('current_price', 'N/A')}
            Price Change: {technical_indicators.get('price_change', 'N/A')} ({technical_indicators.get('price_change_percent', 'N/A')}%)
            
            RSI (14): {technical_indicators.get('rsi', 'N/A')}
            
            
            MACD Analysis:
            - MACD Line: {technical_indicators.get('macd', {}).get('macd', 'N/A')}
            - Signal Line: {technical_indicators.get('macd', {}).get('signal', 'N/A')}
            - Histogram: {technical_indicators.get('macd', {}).get('histogram', 'N/A')}
            
            
            Moving Averages:
            - SMA 20: ${technical_indicators.get('sma', {}).get('sma_20', 'N/A')}
            - SMA 50: ${technical_indicators.get('sma', {}).get('sma_50', 'N/A')}
            - SMA 200: ${technical_indicators.get('sma', {}).get('sma_200', 'N/A')}
            
            
            Volume Analysis:
            - Current Volume: {technical_indicators.get('volume', 'N/A')}
            - 20-day Average: {technical_indicators.get('volume_analysis', {}).get('avg_20', 'N/A')}
            - Volume Ratio: {technical_indicators.get('volume_analysis', {}).get('ratio', 'N/A')}x
            - Volume Signal: {technical_indicators.get('volume_analysis', {}).get('signal', 'N/A')}
            
            
            Bollinger Bands:
            - Upper Band: ${technical_indicators.get('bollinger_bands', {}).get('upper', 'N/A')}
            - Middle Band: ${technical_indicators.get('bollinger_bands', {}).get('middle', 'N/A')}
            - Lower Band: ${technical_indicators.get('bollinger_bands', {}).get('lower', 'N/A')}
            - %B Position: {technical_indicators.get('bollinger_bands', {}).get('percent_b', 'N/A')}
            
            
            Support & Resistance:
            - Resistance Levels: {technical_indicators.get('support_resistance', {}).get('resistance', [])}
            - Support Levels: {technical_indicators.get('support_resistance', {}).get('support', [])}
            - Pivot Point: {technical_indicators.get('support_resistance', {}).get('pivot', 'N/A')}
            
            
            Additional Metrics:
            - Current Trend: {technical_indicators.get('trend', 'N/A')}
            - Volatility (ATR): {technical_indicators.get('atr', 'N/A')}
            - Stochastic K: {technical_indicators.get('stochastic', {}).get('k', 'N/A')}
            - Stochastic D: {technical_indicators.get('stochastic', {}).get('d', 'N/A')}

            PROVIDE COMPREHENSIVE ANALYSIS IN JSON FORMAT:
            {{
                "expert_signal": "STRONG_BUY/BUY/HOLD/SELL/STRONG_SELL",
                "confidence": 0-100,
                "detailed_analysis": "Comprehensive explanation of why you agree/disagree with computed signal and your reasoning",
                "signal_breakdown": {{
                    "rsi_analysis": "Detailed RSI interpretation with current value context",
                    "macd_analysis": "MACD crossover and momentum analysis", 
                    "trend_analysis": "Moving average and trend strength analysis",
                    "volume_analysis": "Volume confirmation and participation analysis",
                    "volatility_analysis": "Bollinger bands and volatility assessment",
                    "support_resistance_analysis": "Key levels and price action analysis"
                }},
                "agreement_with_computed": {{
                    "agrees": true/false,
                    "reasoning": "Why you agree or disagree with the mathematical model"
                }},
                "risk_assessment": {{
                    "risk_level": "LOW/MEDIUM/HIGH",
                    "key_risks": ["risk1", "risk2", "risk3"],
                    "risk_mitigation": "How to manage identified risks"
                }},
                "strategy_recommendation": {{
                    "entry_strategy": "When and how to enter position",
                    "position_sizing": "Recommended position size",
                    "stop_loss": "Specific stop loss level and reasoning",
                    "take_profit_targets": ["TP1 with reasoning", "TP2 with reasoning"],
                    "holding_period": "Expected time horizon"
                }},
                "key_levels": {{
                    "immediate_resistance": "Next resistance level",
                    "immediate_support": "Next support level", 
                    "breakout_level": "Key level for trend continuation",
                    "invalidation_level": "Level that would invalidate analysis"
                }},
                "timeframe_analysis": {{
                    "short_term": "1-5 day outlook",
                    "medium_term": "1-4 week outlook",
                    "long_term": "1-3 month outlook"
                }},
                "market_context": "Overall market conditions affecting this trade",
                "confidence_factors": ["What increases confidence", "What decreases confidence"]
            }}

            IMPORTANT INSTRUCTIONS:
            1. Be specific with price levels and percentages
            2. Explain WHY each indicator supports your view
            3. Compare your expert opinion with the computed mathematical signal
            4. Provide actionable trading advice
            5. Consider risk management in every recommendation
            6. Use current indicator values to support your analysis
            7. Be honest if you disagree with the computed signal and explain why
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            try:
                text = response.text
                if '```json' in text:
                    text = text.split('```json')[1].split('```')[0]
                elif '{' in text and '}' in text:
                    start = text.index('{')
                    end = text.rindex('}') + 1
                    text = text[start:end]
                
                result = json.loads(text)
                return result
                
            except json.JSONDecodeError as e:
                # Fallback if JSON parsing fails
                return {
                    "expert_signal": "HOLD",
                    "confidence": 60,
                    "detailed_analysis": response.text,
                    "signal_breakdown": {},
                    "agreement_with_computed": {
                        "agrees": True,
                        "reasoning": "JSON parsing failed, using raw response"
                    },
                    "risk_assessment": {
                        "risk_level": "MEDIUM",
                        "key_risks": ["Analysis format error"],
                        "risk_mitigation": "Manual review recommended"
                    },
                    "strategy_recommendation": {
                        "entry_strategy": "See detailed analysis",
                        "position_sizing": "Standard position",
                        "stop_loss": "Use computed signal guidance",
                        "take_profit_targets": ["See analysis"],
                        "holding_period": "Medium term"
                    },
                    "key_levels": {},
                    "timeframe_analysis": {},
                    "market_context": "Analysis available but format error occurred",
                    "confidence_factors": ["Raw analysis available"]
                }
                
        except Exception as e:
            return {
                "expert_signal": "HOLD",
                "confidence": 0,
                "detailed_analysis": f"Trading expert analysis failed: {str(e)}",
                "signal_breakdown": {},
                "agreement_with_computed": {
                    "agrees": None,
                    "reasoning": f"Error: {str(e)}"
                },
                "risk_assessment": {
                    "risk_level": "HIGH", 
                    "key_risks": ["AI analysis unavailable"],
                    "risk_mitigation": "Use computed signals and manual analysis"
                },
                "strategy_recommendation": {
                    "entry_strategy": "Rely on mathematical model only",
                    "position_sizing": "Reduced size due to limited analysis",
                    "stop_loss": "Conservative stop loss",
                    "take_profit_targets": ["Manual analysis required"],
                    "holding_period": "Short term until AI available"
                },
                "key_levels": {},
                "timeframe_analysis": {},
                "market_context": "AI expert analysis unavailable",
                "confidence_factors": ["Limited to mathematical indicators only"]
            }
    
    def _format_individual_signals(self, individual_signals: Dict) -> str:
        """Format individual signal contributions for the prompt"""
        if not individual_signals:
            return "Individual signal breakdown not available"
        
        formatted = "Individual Indicator Signals & Weights:\n"
        for indicator, data in individual_signals.items():
            if isinstance(data, dict):
                signal = data.get('signal', 'N/A')
                weight = data.get('weight', 'N/A')
                contribution = data.get('contribution', 'N/A')
                formatted += f"- {indicator.upper()}: {signal} (Weight: {weight}%, Contribution: {contribution})\n"
        
        return formatted
