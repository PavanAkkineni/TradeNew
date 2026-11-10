"""
Fundamental Analysis Module
Analyzes financial statements and company metrics
"""
from typing import Dict, Any, Optional

class FundamentalAnalyzer:
    """
    Analyze fundamental data including financial statements,
    ratios, and company metrics
    """
    
    def __init__(self):
        # Industry averages for comparison (technology sector)
        self.industry_benchmarks = {
            'pe_ratio': 25,
            'profit_margin': 15,
            'roe': 15,
            'debt_to_equity': 1.0,
            'current_ratio': 1.5,
            'revenue_growth': 10
        }
    
    def analyze(self, fundamental_data: Dict) -> Dict[str, Any]:
        """
        Comprehensive fundamental analysis
        """
        if not fundamental_data:
            return {}
        
        overview = fundamental_data.get('overview', {})
        income = fundamental_data.get('income', {})
        balance = fundamental_data.get('balance', {})
        cash_flow = fundamental_data.get('cash_flow', {})
        earnings = fundamental_data.get('earnings', {})
        
        # Calculate key metrics
        metrics = {}
        
        # Valuation metrics
        metrics['pe_ratio'] = self._safe_float(overview.get('PERatio', 0))
        metrics['peg_ratio'] = self._safe_float(overview.get('PEGRatio', 0))
        metrics['price_to_book'] = self._safe_float(overview.get('PriceToBookRatio', 0))
        metrics['price_to_sales'] = self._safe_float(overview.get('PriceToSalesRatioTTM', 0))
        metrics['ev_to_revenue'] = self._safe_float(overview.get('EVToRevenue', 0))
        metrics['ev_to_ebitda'] = self._safe_float(overview.get('EVToEBITDA', 0))
        
        # EPS
        metrics['eps'] = self._safe_float(overview.get('EPS', 0))
        
        # Profitability metrics
        metrics['profit_margin'] = self._safe_float(overview.get('ProfitMargin', 0)) * 100
        metrics['operating_margin'] = self._safe_float(overview.get('OperatingMarginTTM', 0)) * 100
        
        # Calculate gross margin
        revenue_ttm = self._safe_float(overview.get('RevenueTTM', 0))
        gross_profit_ttm = self._safe_float(overview.get('GrossProfitTTM', 0))
        if revenue_ttm > 0:
            metrics['gross_margin'] = (gross_profit_ttm / revenue_ttm) * 100
        else:
            metrics['gross_margin'] = 0
        
        metrics['roe'] = self._safe_float(overview.get('ReturnOnEquityTTM', 0)) * 100
        metrics['roa'] = self._safe_float(overview.get('ReturnOnAssetsTTM', 0)) * 100
        
        # Growth metrics
        metrics['revenue_growth'] = self._calculate_revenue_growth(income)
        metrics['earnings_growth'] = self._calculate_earnings_growth(income)
        metrics['quarterly_revenue_growth'] = self._safe_float(overview.get('QuarterlyRevenueGrowthYOY', 0)) * 100
        metrics['quarterly_earnings_growth'] = self._safe_float(overview.get('QuarterlyEarningsGrowthYOY', 0)) * 100
        
        # Financial health
        metrics['debt_to_equity'] = self._calculate_debt_to_equity(balance)
        metrics['current_ratio'] = self._calculate_current_ratio(balance)
        metrics['quick_ratio'] = self._calculate_quick_ratio(balance)
        
        # Dividend metrics
        metrics['dividend_yield'] = self._safe_float(overview.get('DividendYield', 0)) * 100
        metrics['dividend_payout_ratio'] = self._safe_float(overview.get('PayoutRatio', 0)) * 100
        
        # Calculate scores
        valuation_score = self._calculate_valuation_score(metrics)
        profitability_score = self._calculate_profitability_score(metrics)
        growth_score = self._calculate_growth_score(metrics)
        health_score = self._calculate_health_score(metrics)
        
        # Overall fundamental score
        overall_score = (valuation_score * 0.25 + 
                        profitability_score * 0.35 + 
                        growth_score * 0.25 + 
                        health_score * 0.15)
        
        return {
            'metrics': metrics,
            'scores': {
                'valuation': valuation_score,
                'profitability': profitability_score,
                'growth': growth_score,
                'health': health_score,
                'overall': overall_score
            },
            'interpretation': self._interpret_scores(overall_score),
            'sector_avg_pe': self.industry_benchmarks['pe_ratio'],
            **metrics  # Include individual metrics for signal generation
        }
    
    def _safe_float(self, value: Any, default: float = 0) -> float:
        """Safely convert to float"""
        try:
            if value == 'None' or value is None:
                return default
            return float(value)
        except:
            return default
    
    def _calculate_revenue_growth(self, income_data: Dict) -> float:
        """Calculate year-over-year revenue growth"""
        if not income_data or 'annualReports' not in income_data:
            return 0
        
        reports = income_data['annualReports']
        if len(reports) < 2:
            return 0
        
        try:
            current_revenue = float(reports[0].get('totalRevenue', 0))
            previous_revenue = float(reports[1].get('totalRevenue', 0))
            
            if previous_revenue == 0:
                return 0
            
            growth = ((current_revenue - previous_revenue) / previous_revenue) * 100
            return round(growth, 2)
        except:
            return 0
    
    def _calculate_earnings_growth(self, income_data: Dict) -> float:
        """Calculate year-over-year earnings growth"""
        if not income_data or 'annualReports' not in income_data:
            return 0
        
        reports = income_data['annualReports']
        if len(reports) < 2:
            return 0
        
        try:
            current_earnings = float(reports[0].get('netIncome', 0))
            previous_earnings = float(reports[1].get('netIncome', 0))
            
            if previous_earnings == 0:
                return 0
            
            growth = ((current_earnings - previous_earnings) / previous_earnings) * 100
            return round(growth, 2)
        except:
            return 0
    
    def _calculate_debt_to_equity(self, balance_data: Dict) -> float:
        """Calculate debt to equity ratio"""
        if not balance_data or 'annualReports' not in balance_data:
            return 0
        
        # Uses actual borrowings, not total liabilities: total liabilities also
        # include pensions, leases, payables and deferred revenue, which made
        # mature companies (e.g. IBM) look far more indebted than they are.
        # Returns None when equity is zero/negative (common after big buybacks),
        # where the ratio is meaningless.
        try:
            latest = balance_data['annualReports'][0]
            total_equity = self._safe_float(latest.get('totalShareholderEquity'), 0)
            debt = self._safe_float(latest.get('shortLongTermDebtTotal'), None)
            if debt is None:
                debt = (self._safe_float(latest.get('shortTermDebt'))
                        + self._safe_float(latest.get('longTermDebt')))
            if total_equity <= 0:
                return None
            return round(debt / total_equity, 2)
        except Exception:
            return None
    
    def _calculate_current_ratio(self, balance_data: Dict) -> float:
        """Calculate current ratio (current assets / current liabilities)"""
        if not balance_data or 'annualReports' not in balance_data:
            return 0
        
        try:
            latest = balance_data['annualReports'][0]
            current_assets = float(latest.get('totalCurrentAssets', 0))
            current_liabilities = float(latest.get('totalCurrentLiabilities', 0))
            
            if current_liabilities == 0:
                return 0
            
            return round(current_assets / current_liabilities, 2)
        except:
            return 0
    
    def _calculate_quick_ratio(self, balance_data: Dict) -> float:
        """Calculate quick ratio (liquid assets / current liabilities)"""
        if not balance_data or 'annualReports' not in balance_data:
            return 0
        
        try:
            latest = balance_data['annualReports'][0]
            current_assets = float(latest.get('totalCurrentAssets', 0))
            inventory = float(latest.get('inventory', 0))
            current_liabilities = float(latest.get('totalCurrentLiabilities', 0))
            
            if current_liabilities == 0:
                return 0
            
            quick_assets = current_assets - inventory
            return round(quick_assets / current_liabilities, 2)
        except:
            return 0
    
    def _calculate_valuation_score(self, metrics: Dict) -> float:
        """Score valuation metrics (0-100)"""
        score = 50  # Start neutral
        
        # P/E ratio comparison
        pe_ratio = metrics.get('pe_ratio', 0)
        if 0 < pe_ratio < self.industry_benchmarks['pe_ratio'] * 0.8:
            score += 20  # Undervalued
        elif pe_ratio > self.industry_benchmarks['pe_ratio'] * 1.5:
            score -= 20  # Overvalued
        
        # PEG ratio
        peg = metrics.get('peg_ratio', 0)
        if 0 < peg < 1:
            score += 15  # Good value
        elif peg > 2:
            score -= 15  # Poor value
        
        # Price to Book
        pb = metrics.get('price_to_book', 0)
        if 0 < pb < 1:
            score += 15  # Trading below book value
        elif pb > 5:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_profitability_score(self, metrics: Dict) -> float:
        """Score profitability metrics (0-100)"""
        score = 50  # Start neutral
        
        # ROE
        roe = metrics.get('roe', 0)
        if roe > self.industry_benchmarks['roe']:
            score += 20
        elif roe < self.industry_benchmarks['roe'] * 0.5:
            score -= 20
        
        # Profit margin
        margin = metrics.get('profit_margin', 0)
        if margin > self.industry_benchmarks['profit_margin']:
            score += 20
        elif margin < 5:
            score -= 20
        
        # Operating margin trend
        op_margin = metrics.get('operating_margin', 0)
        if op_margin > 20:
            score += 10
        elif op_margin < 10:
            score -= 10
        
        return max(0, min(100, score))
    
    def _calculate_growth_score(self, metrics: Dict) -> float:
        """Score growth metrics (0-100)"""
        score = 50  # Start neutral
        
        # Revenue growth
        rev_growth = metrics.get('revenue_growth', 0)
        if rev_growth > self.industry_benchmarks['revenue_growth']:
            score += 25
        elif rev_growth < 0:
            score -= 25
        
        # Earnings growth
        earn_growth = metrics.get('earnings_growth', 0)
        if earn_growth > 15:
            score += 25
        elif earn_growth < 0:
            score -= 25
        
        return max(0, min(100, score))
    
    def _calculate_health_score(self, metrics: Dict) -> float:
        """Score financial health metrics (0-100)"""
        score = 50  # Start neutral
        
        # Debt to equity
        de = metrics.get('debt_to_equity')
        if de is None:
            pass  # negative/zero equity: ratio not meaningful, stay neutral
        elif de < self.industry_benchmarks['debt_to_equity'] * 0.5:
            score += 25
        elif de > self.industry_benchmarks['debt_to_equity'] * 2:
            score -= 25
        
        # Current ratio
        current = metrics.get('current_ratio', 0)
        if current > self.industry_benchmarks['current_ratio']:
            score += 25
        elif current < 1:
            score -= 25
        
        return max(0, min(100, score))
    
    def _interpret_scores(self, overall_score: float) -> str:
        """Interpret the overall fundamental score"""
        if overall_score >= 75:
            return "Excellent fundamentals - Strong buy candidate"
        elif overall_score >= 60:
            return "Good fundamentals - Consider buying"
        elif overall_score >= 40:
            return "Average fundamentals - Neutral"
        elif overall_score >= 25:
            return "Weak fundamentals - Consider selling"
        else:
            return "Poor fundamentals - Strong sell candidate"
