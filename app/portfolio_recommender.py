"""
Component 3: Portfolio Recommendation Engine (Gemini-Powered)
This component takes user profile and market data, sends it to Gemini,
and receives structured portfolio allocation recommendations.
"""
import os
import json
import logging
from typing import Dict, Any, Optional
import google.generativeai as genai

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortfolioRecommender:
    """
    Gemini-powered portfolio recommendation engine.
    Generates personalized portfolio allocations based on user profile and market data.
    """
    
    def __init__(self):
        """Initialize with Gemini API key"""
        self.api_key = "AIzaSyA4dxyFk6yViXiuzzTvPdaIaSzNNJz6tB4"
        if self.api_key:
            genai.configure(api_key=self.api_key)
            logger.info("✅ Gemini API configured")
        else:
            logger.warning("⚠️ GOOGLE_API_KEY not found")
        
        # Model configuration
        # Using gemini-2.5-flash for fast, cost-effective generation
        self.model_name = "gemini-2.5-pro"
        
    def generate_portfolio_recommendation(
        self, 
        user_profile: Dict[str, Any], 
        market_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate portfolio recommendation using Gemini AI
        
        Args:
            user_profile: User's investment profile
            market_data: Current market data
            
        Returns:
            Structured portfolio recommendation with allocation and justification
        """
        if not self.api_key:
            return {
                'error': 'Gemini API key not configured',
                'allocation': None,
                'justification': None
            }
        
        logger.info("🤖 Generating portfolio recommendation with Gemini...")
        
        try:
            # Define response schema for structured output
            response_schema = {
                "type": "object",
                "properties": {
                    "portfolio_allocation": {
                        "type": "object",
                        "properties": {
                            "stocks_etfs": {
                                "type": "object",
                                "properties": {
                                    "percentage": {"type": "number"},
                                    "amount": {"type": "number"}
                                }
                            },
                            "bonds_fixed_income": {
                                "type": "object",
                                "properties": {
                                    "percentage": {"type": "number"},
                                    "amount": {"type": "number"}
                                }
                            },
                            "real_estate": {
                                "type": "object",
                                "properties": {
                                    "percentage": {"type": "number"},
                                    "amount": {"type": "number"}
                                }
                            },
                            "commodities_gold": {
                                "type": "object",
                                "properties": {
                                    "percentage": {"type": "number"},
                                    "amount": {"type": "number"}
                                }
                            },
                            "cash_equivalents": {
                                "type": "object",
                                "properties": {
                                    "percentage": {"type": "number"},
                                    "amount": {"type": "number"}
                                }
                            }
                        }
                    },
                    "justification": {
                        "type": "object",
                        "properties": {
                            "overall_strategy": {"type": "string"},
                            "risk_assessment": {"type": "string"},
                            "market_conditions_impact": {"type": "string"},
                            "time_horizon_considerations": {"type": "string"},
                            "key_recommendations": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    },
                    "expected_returns": {
                        "type": "object",
                        "properties": {
                            "conservative_estimate": {"type": "string"},
                            "moderate_estimate": {"type": "string"},
                            "optimistic_estimate": {"type": "string"}
                        }
                    }
                },
                "required": ["portfolio_allocation", "justification", "expected_returns"]
            }
            
            # Construct the prompt
            system_instruction = self._create_system_instruction()
            user_prompt = self._create_user_prompt(user_profile, market_data)
            
            # Configure model with response schema
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.95,
                    "top_k": 40,
                    "max_output_tokens": 8192,
                    "response_mime_type": "application/json",
                    "response_schema": response_schema
                },
                system_instruction=system_instruction
            )
            
            # Generate response
            logger.info("📤 Sending request to Gemini...")
            response = model.generate_content(user_prompt)
            
            # Parse JSON response
            result = json.loads(response.text)
            logger.info("✅ Portfolio recommendation generated successfully")
            
            return {
                'success': True,
                'recommendation': result,
                'user_profile': user_profile
            }
            
        except Exception as e:
            logger.error(f"❌ Error generating recommendation: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'recommendation': None
            }
    
    def _create_system_instruction(self) -> str:
        """Create system instruction for Gemini"""
        return """You are 'Aura', an expert financial advisor AI assistant. Your task is to create personalized investment portfolio allocations.

CRITICAL RULES:
1. Base your entire analysis ONLY on the provided user profile and real-time market data
2. Do NOT use any outside knowledge or assumptions
3. Adhere strictly to the JSON output schema
4. All percentages must sum to 100%
5. Be professional, clear, and encouraging
6. Provide specific, actionable recommendations

ASSET CLASSES:
- Stocks/ETFs: Equity investments (S&P 500, growth stocks)
- Bonds/Fixed Income: Treasury bonds, corporate bonds
- Real Estate: REITs, real estate ETFs
- Commodities/Gold: Gold, precious metals
- Cash Equivalents: Money market, savings

RISK PROFILES:
- Conservative: 40-50% stocks, 40-50% bonds, 10-20% other
- Moderate: 60-70% stocks, 20-30% bonds, 10% other
- Aggressive: 80-90% stocks, 5-10% bonds, 5-10% other

Adjust based on:
- Time horizon (longer = more aggressive possible)
- Current market conditions (volatility, interest rates)
- Economic indicators (inflation, growth)
- Market sentiment (news, trends)"""
    
    def _create_user_prompt(
        self, 
        user_profile: Dict[str, Any], 
        market_data: Dict[str, Any]
    ) -> str:
        """Create user prompt combining profile and market data"""
        
        # Extract and format market data
        econ = market_data.get('economic_indicators', {})
        perf = market_data.get('market_performance', {})
        sent = market_data.get('market_sentiment', {})
        
        # Format economic indicators
        inflation = econ.get('inflation_rate', {}).get('value', 'N/A')
        fed_rate = econ.get('federal_funds_rate', {}).get('value', 'N/A')
        gdp = econ.get('gdp_growth_rate', {}).get('value', 'N/A')
        unemployment = econ.get('unemployment_rate', {}).get('value', 'N/A')
        
        # Format market performance
        sp500 = perf.get('sp500', {}).get('current_price', 'N/A')
        sp500_ma50 = perf.get('sp500', {}).get('ma_50', 'N/A')
        vix = perf.get('vix', {}).get('current_price', 'N/A')
        treasury = perf.get('treasury_10y', {}).get('current_price', 'N/A')
        gold = perf.get('gold', {}).get('current_price', 'N/A')
        realestate = perf.get('vnq', {}).get('current_price', 'N/A')
        
        # Format headlines
        headlines = sent.get('headlines', [])
        headline_texts = [h.get('title', '') for h in headlines[:5]]
        
        prompt = f"""Generate a personalized investment portfolio allocation based on the following information:

USER PROFILE:
- Investment Capital: ${user_profile.get('investment_capital', 0):,.2f}
- Target Amount: ${user_profile.get('target_amount', 0):,.2f}
- Time Horizon: {user_profile.get('time_horizon', 0)} years
- Risk Appetite: {user_profile.get('risk_appetite', 'Unknown')}

CURRENT MARKET DATA:

Economic Indicators:
- Inflation (CPI): {inflation}
- Federal Funds Rate: {fed_rate}%
- GDP Growth: {gdp}%
- Unemployment: {unemployment}%

Market Performance:
- S&P 500 (SPY): ${sp500} (50-day MA: ${sp500_ma50})
- Market Volatility (VXX): ${vix}
- Treasury Bond (TLT): ${treasury}
- Gold (GLD): ${gold}
- Real Estate (VNQ): ${realestate}

Recent Market Sentiment (Headlines):
{chr(10).join(f'- {h}' for h in headline_texts if h)}

TASK:
Based on this data, create a portfolio allocation that:
1. Matches the user's risk appetite ({user_profile.get('risk_appetite', 'Unknown')})
2. Is appropriate for their time horizon ({user_profile.get('time_horizon', 0)} years)
3. Considers current market conditions (inflation: {inflation}, rates: {fed_rate}%, volatility: {vix})
4. Helps them reach ${user_profile.get('target_amount', 0):,.2f} from ${user_profile.get('investment_capital', 0):,.2f}
5. Provides clear justification for each decision

Return a structured JSON response following the schema."""

        return prompt


# Standalone test function
if __name__ == "__main__":
    """Test the portfolio recommender"""
    recommender = PortfolioRecommender()
    
    # Test data
    test_profile = {
        'investment_capital': 50000,
        'target_amount': 100000,
        'time_horizon': 7,
        'risk_appetite': 'moderate'
    }
    
    test_market_data = {
        'economic_indicators': {
            'inflation_rate': {'value': 3.1},
            'federal_funds_rate': {'value': 5.25},
            'gdp_growth_rate': {'value': 2.1},
            'unemployment_rate': {'value': 3.8}
        },
        'market_performance': {
            'sp500': {'current_price': 653.02, 'ma_50': 650.00},
            'vix': {'current_price': 37.47},
            'treasury_10y': {'current_price': 90.62},
            'gold': {'current_price': 369.12},
            'vnq': {'current_price': 88.13}
        },
        'market_sentiment': {
            'headlines': [
                {'title': 'Markets Rally on Strong Jobs Report'},
                {'title': 'Fed Signals Pause in Rate Hikes'}
            ]
        }
    }
    
    result = recommender.generate_portfolio_recommendation(test_profile, test_market_data)
    print(json.dumps(result, indent=2))

