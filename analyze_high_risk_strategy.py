"""
HIGH RISK HIGH REWARD STRATEGY
- Executes on WEAK signals (WEAK_BUY, WEAK_SELL)
- More aggressive trading
- Higher position sizes
- Initial Capital: $10,000
"""

import json
from pathlib import Path

# CONFIGURATION
INITIAL_CAPITAL = 10000.0
COMMISSION_RATE = 0.0  # 0% commission for simplicity

# ============================================================================
# PORTFOLIO MANAGEMENT
# ============================================================================

class Portfolio:
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.transactions = []
        self.daily_values = []
    
    def buy(self, date, price, signal, reason):
        """Buy as many shares as possible with available cash"""
        if self.cash < price:
            return False
        
        # High risk: Use 95% of available cash
        max_to_spend = self.cash * 0.95
        shares_to_buy = int(max_to_spend / price)
        
        if shares_to_buy < 1:
            return False
        
        cost = shares_to_buy * price
        commission = cost * COMMISSION_RATE
        total_cost = cost + commission
        
        self.cash -= total_cost
        self.shares += shares_to_buy
        
        self.transactions.append({
            'date': date,
            'action': 'BUY',
            'signal': signal,
            'shares': shares_to_buy,
            'price': price,
            'cost': cost,
            'commission': commission,
            'total_cost': total_cost,
            'cash_after': self.cash,
            'shares_after': self.shares,
            'reason': reason
        })
        
        return True
    
    def sell(self, date, price, signal, reason):
        """Sell all shares"""
        if self.shares == 0:
            return False
        
        proceeds = self.shares * price
        commission = proceeds * COMMISSION_RATE
        net_proceeds = proceeds - commission
        
        self.transactions.append({
            'date': date,
            'action': 'SELL',
            'signal': signal,
            'shares': self.shares,
            'price': price,
            'proceeds': proceeds,
            'commission': commission,
            'net_proceeds': net_proceeds,
            'cash_after': self.cash + net_proceeds,
            'shares_after': 0,
            'reason': reason
        })
        
        self.cash += net_proceeds
        self.shares = 0
        
        return True
    
    def get_total_value(self, current_price):
        """Calculate total portfolio value"""
        return self.cash + (self.shares * current_price)
    
    def record_daily_value(self, date, current_price):
        """Record portfolio value for the day"""
        total_value = self.get_total_value(current_price)
        self.daily_values.append({
            'date': date,
            'cash': self.cash,
            'shares': self.shares,
            'price': current_price,
            'total_value': total_value
        })

# ============================================================================
# HIGH RISK TRADING STRATEGY
# ============================================================================

def execute_high_risk_strategy(signals_data):
    """
    HIGH RISK Strategy Rules:
    - STRONG_BUY: Buy aggressively
    - BUY: Buy aggressively
    - WEAK_BUY: Buy (unlike conservative, we trade on weak signals)
    - HOLD: Hold position
    - WEAK_SELL: Sell immediately (don't wait for losses)
    - SELL: Sell immediately
    - STRONG_SELL: Sell immediately
    """
    
    portfolio = Portfolio(INITIAL_CAPITAL)
    position_entry_price = None
    
    print("=" * 100)
    print("HIGH RISK HIGH REWARD STRATEGY - $10,000 CAPITAL")
    print("=" * 100)
    print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"Commission Rate: {COMMISSION_RATE * 100:.2f}%")
    print(f"Strategy: Aggressive - Execute on ALL buy/sell signals including WEAK")
    print("=" * 100)
    print()
    
    for day_data in signals_data:
        date = day_data['date']
        price = day_data['price']
        signal = day_data['signal']
        confidence = day_data['confidence']
        reasons = day_data['reasons']
        
        # Track daily value
        portfolio.record_daily_value(date, price)
        
        # Determine action based on signal
        action_taken = "HOLD"
        action_reason = ""
        
        # BUY SIGNALS - Execute on all buy signals including WEAK
        if signal in ['STRONG_BUY', 'BUY', 'WEAK_BUY']:
            if portfolio.shares == 0 and portfolio.cash > 0:
                tech_reasons = reasons.get('technical', [])
                
                if signal == 'STRONG_BUY':
                    action_reason = f"Strong bullish signal. {' | '.join(tech_reasons[:2])}"
                elif signal == 'BUY':
                    action_reason = f"Bullish signal. {' | '.join(tech_reasons[:2])}"
                else:  # WEAK_BUY
                    action_reason = f"Weak bullish - HIGH RISK entry. {' | '.join(tech_reasons[:1])}"
                
                if portfolio.buy(date, price, signal, action_reason):
                    position_entry_price = price
                    action_taken = f"BUY {portfolio.shares} shares"
        
        # SELL SIGNALS - Execute on all sell signals including WEAK
        elif signal in ['WEAK_SELL', 'SELL', 'STRONG_SELL']:
            if portfolio.shares > 0:
                tech_reasons = reasons.get('technical', [])
                
                if signal == 'STRONG_SELL':
                    action_reason = f"Strong bearish signal. {' | '.join(tech_reasons[:2])}"
                elif signal == 'SELL':
                    action_reason = f"Bearish signal. {' | '.join(tech_reasons[:2])}"
                else:  # WEAK_SELL
                    action_reason = f"Weak bearish - HIGH RISK exit. {' | '.join(tech_reasons[:1])}"
                
                if portfolio.sell(date, price, signal, action_reason):
                    if position_entry_price:
                        profit_loss = ((price - position_entry_price) / position_entry_price) * 100
                        action_taken = f"SELL {portfolio.transactions[-1]['shares']} shares (P/L: {profit_loss:.2f}%)"
                    else:
                        action_taken = f"SELL {portfolio.transactions[-1]['shares']} shares"
                    position_entry_price = None
        
        # Print daily status
        total_value = portfolio.get_total_value(price)
        return_pct = ((total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        
        print(f"📅 {date} | ${price:6.2f} | {signal:12s} ({confidence:.0f}%) | {action_taken:30s} | Value: ${total_value:9.2f} ({return_pct:+6.2f}%)")
        
        if action_taken != "HOLD":
            print(f"   💡 {action_reason}")
            print()
    
    return portfolio

# ============================================================================
# PERFORMANCE ANALYSIS
# ============================================================================

def analyze_performance(portfolio, signals_data):
    """Analyze and print performance metrics"""
    
    if not portfolio.daily_values:
        print("No data to analyze")
        return
    
    print()
    print("=" * 100)
    print("HIGH RISK STRATEGY - PERFORMANCE SUMMARY")
    print("=" * 100)
    
    initial_value = portfolio.initial_capital
    final_value = portfolio.daily_values[-1]['total_value']
    total_return = final_value - initial_value
    total_return_pct = (total_return / initial_value) * 100
    
    print(f"\n💰 RETURNS:")
    print(f"   Initial Capital:  ${initial_value:,.2f}")
    print(f"   Final Value:      ${final_value:,.2f}")
    print(f"   Total Return:     ${total_return:,.2f} ({total_return_pct:+.2f}%)")
    
    # Trade statistics
    num_trades = len([t for t in portfolio.transactions if t['action'] == 'BUY'])
    print(f"\n📊 TRADING ACTIVITY:")
    print(f"   Total Trades:     {num_trades}")
    print(f"   Transactions:     {len(portfolio.transactions)}")
    
    # Calculate win rate
    completed_trades = []
    buy_price = None
    for t in portfolio.transactions:
        if t['action'] == 'BUY':
            buy_price = t['price']
        elif t['action'] == 'SELL' and buy_price:
            profit = ((t['price'] - buy_price) / buy_price) * 100
            completed_trades.append(profit)
            buy_price = None
    
    if completed_trades:
        wins = len([p for p in completed_trades if p > 0])
        win_rate = (wins / len(completed_trades)) * 100
        avg_profit = sum(completed_trades) / len(completed_trades)
        print(f"   Completed Trades: {len(completed_trades)}")
        print(f"   Win Rate:         {win_rate:.1f}%")
        print(f"   Avg Trade:        {avg_profit:+.2f}%")
    
    # Calculate max drawdown
    peak_value = initial_value
    max_drawdown = 0
    for dv in portfolio.daily_values:
        if dv['total_value'] > peak_value:
            peak_value = dv['total_value']
        drawdown = ((dv['total_value'] - peak_value) / peak_value) * 100
        if drawdown < max_drawdown:
            max_drawdown = drawdown
    
    print(f"\n📉 RISK METRICS:")
    print(f"   Max Drawdown:     {max_drawdown:.2f}%")
    
    # Buy and hold comparison
    first_price = signals_data[0]['price']
    last_price = signals_data[-1]['price']
    buy_hold_return = ((last_price - first_price) / first_price) * 100
    outperformance = total_return_pct - buy_hold_return
    
    print(f"\n🎯 BENCHMARK COMPARISON:")
    print(f"   Buy-and-Hold:     {buy_hold_return:+.2f}%")
    print(f"   Strategy:         {total_return_pct:+.2f}%")
    print(f"   Outperformance:   {outperformance:+.2f}%")
    
    if outperformance > 0:
        print(f"   Result:           ✅ BEAT THE BENCHMARK by {outperformance:.2f}%")
    else:
        print(f"   Result:           ❌ UNDERPERFORMED by {abs(outperformance):.2f}%")
    
    print()
    print("=" * 100)
    
    return {
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'win_rate': win_rate if completed_trades else 0,
        'max_drawdown': max_drawdown,
        'num_trades': num_trades,
        'buy_hold_return': buy_hold_return,
        'outperformance': outperformance
    }

def save_results(portfolio, metrics):
    """Save results to JSON files"""
    
    # Save transactions
    with open('high_risk_transactions.json', 'w') as f:
        json.dump(portfolio.transactions, f, indent=2)
    
    # Save daily values
    with open('high_risk_daily_values.json', 'w') as f:
        json.dump(portfolio.daily_values, f, indent=2)
    
    # Save metrics
    with open('high_risk_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Results saved:")
    print(f"   - high_risk_transactions.json")
    print(f"   - high_risk_daily_values.json")
    print(f"   - high_risk_metrics.json")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 100)
    print("HIGH RISK HIGH REWARD BACKTEST - IBM (Sept 3 - Oct 3, 2025)")
    print("=" * 100)
    print()
    
    # Load signals from backtest_results.json
    try:
        with open('backtest_results.json', 'r') as f:
            signals_data = json.load(f)
        
        print(f"✅ Loaded {len(signals_data)} daily signals from backtest_results.json")
        print()
        
        # Execute high risk strategy
        portfolio = execute_high_risk_strategy(signals_data)
        
        # Analyze performance
        metrics = analyze_performance(portfolio, signals_data)
        
        # Save results
        save_results(portfolio, metrics)
        
        print("\n✅ HIGH RISK STRATEGY ANALYSIS COMPLETE!")
        
    except FileNotFoundError:
        print("❌ Error: backtest_results.json not found!")
        print("   Please run backtest_signals.py first to generate signals.")
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
