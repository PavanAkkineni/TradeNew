"""
Backtest Performance Analysis
==============================
Executes trades based on generated signals and calculates returns
Starting capital: $1000
"""

import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

INITIAL_CAPITAL = 1000.0
COMMISSION_RATE = 0.0  # No commission for simplicity (can adjust to 0.001 for 0.1%)

# ============================================================================
# TRADING EXECUTION LOGIC
# ============================================================================

class Portfolio:
    """Manages portfolio state and executions"""
    
    def __init__(self, initial_capital):
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.shares = 0
        self.transactions = []
        self.daily_values = []
        
    def buy(self, date, price, signal, reason=""):
        """Execute buy order"""
        if self.cash <= 0:
            return False
        
        # Buy as many shares as possible with available cash
        shares_to_buy = int(self.cash / price)
        if shares_to_buy <= 0:
            return False
        
        cost = shares_to_buy * price
        commission = cost * COMMISSION_RATE
        total_cost = cost + commission
        
        self.cash -= total_cost
        self.shares += shares_to_buy
        
        transaction = {
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
        }
        self.transactions.append(transaction)
        
        return True
    
    def sell(self, date, price, signal, reason=""):
        """Execute sell order"""
        if self.shares <= 0:
            return False
        
        shares_to_sell = self.shares
        proceeds = shares_to_sell * price
        commission = proceeds * COMMISSION_RATE
        total_proceeds = proceeds - commission
        
        self.cash += total_proceeds
        self.shares = 0
        
        transaction = {
            'date': date,
            'action': 'SELL',
            'signal': signal,
            'shares': shares_to_sell,
            'price': price,
            'proceeds': proceeds,
            'commission': commission,
            'total_proceeds': total_proceeds,
            'cash_after': self.cash,
            'shares_after': self.shares,
            'reason': reason
        }
        self.transactions.append(transaction)
        
        return True
    
    def get_total_value(self, current_price):
        """Calculate total portfolio value"""
        return self.cash + (self.shares * current_price)
    
    def record_daily_value(self, date, price):
        """Record daily portfolio value"""
        total_value = self.get_total_value(price)
        self.daily_values.append({
            'date': date,
            'price': price,
            'cash': self.cash,
            'shares': self.shares,
            'stock_value': self.shares * price,
            'total_value': total_value,
            'return_pct': ((total_value - self.initial_capital) / self.initial_capital) * 100
        })

# ============================================================================
# TRADING STRATEGY
# ============================================================================

def execute_strategy(signals_data):
    """
    Execute trading strategy based on signals
    
    Strategy Rules:
    - STRONG_BUY or BUY: Buy if we have cash and no position
    - WEAK_BUY: Hold if we have position, buy if we don't
    - HOLD: Do nothing
    - WEAK_SELL: Hold if profitable, sell if losing
    - SELL or STRONG_SELL: Sell entire position
    """
    
    portfolio = Portfolio(INITIAL_CAPITAL)
    position_entry_price = None
    
    print("=" * 100)
    print("EXECUTING TRADES BASED ON SIGNALS")
    print("=" * 100)
    print(f"Initial Capital: ${INITIAL_CAPITAL:,.2f}")
    print(f"Commission Rate: {COMMISSION_RATE * 100:.2f}%")
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
        
        if signal in ['STRONG_BUY', 'BUY']:
            # Strong buy signals - buy if we have cash
            if portfolio.shares == 0 and portfolio.cash > 0:
                tech_reasons = reasons.get('technical', [])
                fund_reasons = reasons.get('fundamental', [])
                action_reason = f"Strong bullish signal. {' | '.join(tech_reasons[:2])}"
                
                if portfolio.buy(date, price, signal, action_reason):
                    position_entry_price = price
                    action_taken = f"BUY {portfolio.shares} shares"
                    
        elif signal == 'WEAK_BUY':
            # Weak buy - only buy if we don't have position
            if portfolio.shares == 0 and portfolio.cash > price * 2:  # Need enough for at least 2 shares
                tech_reasons = reasons.get('technical', [])
                action_reason = f"Weak bullish signal. {' | '.join(tech_reasons[:1])}"
                
                if portfolio.buy(date, price, signal, action_reason):
                    position_entry_price = price
                    action_taken = f"BUY {portfolio.shares} shares"
        
        elif signal in ['WEAK_SELL', 'SELL', 'STRONG_SELL']:
            # Sell signals
            if portfolio.shares > 0:
                tech_reasons = reasons.get('technical', [])
                
                # For WEAK_SELL, only sell if losing money
                if signal == 'WEAK_SELL':
                    if position_entry_price and price < position_entry_price * 0.98:  # Down 2%+
                        action_reason = f"Cut losses. {' | '.join(tech_reasons[:1])}"
                        if portfolio.sell(date, price, signal, action_reason):
                            profit_loss = ((price - position_entry_price) / position_entry_price) * 100
                            action_taken = f"SELL {portfolio.transactions[-1]['shares']} shares (P/L: {profit_loss:.2f}%)"
                            position_entry_price = None
                
                # For SELL and STRONG_SELL, always sell
                elif signal in ['SELL', 'STRONG_SELL']:
                    action_reason = f"Strong bearish signal. {' | '.join(tech_reasons[:2])}"
                    if portfolio.sell(date, price, signal, action_reason):
                        profit_loss = ((price - position_entry_price) / position_entry_price) * 100 if position_entry_price else 0
                        action_taken = f"SELL {portfolio.transactions[-1]['shares']} shares (P/L: {profit_loss:.2f}%)"
                        position_entry_price = None
        
        # Print daily status
        total_value = portfolio.get_total_value(price)
        return_pct = ((total_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
        
        print(f"📅 {date} | ${price:6.2f} | {signal:12s} ({confidence:.0f}%) | {action_taken:30s} | Value: ${total_value:8.2f} ({return_pct:+6.2f}%)")
        
        if action_taken != "HOLD":
            print(f"   💡 Reason: {action_reason}")
            print()
    
    return portfolio

# ============================================================================
# PERFORMANCE ANALYSIS
# ============================================================================

def analyze_performance(portfolio):
    """Analyze and display performance metrics"""
    
    print("\n" + "=" * 100)
    print("PERFORMANCE ANALYSIS")
    print("=" * 100)
    
    # Calculate metrics
    final_value = portfolio.daily_values[-1]['total_value']
    total_return = final_value - INITIAL_CAPITAL
    total_return_pct = (total_return / INITIAL_CAPITAL) * 100
    
    # Transaction analysis
    num_trades = len(portfolio.transactions)
    buy_trades = [t for t in portfolio.transactions if t['action'] == 'BUY']
    sell_trades = [t for t in portfolio.transactions if t['action'] == 'SELL']
    
    # Calculate win rate
    winning_trades = 0
    losing_trades = 0
    total_profit = 0
    total_loss = 0
    
    for sell in sell_trades:
        # Find corresponding buy
        buy = None
        for b in reversed(buy_trades):
            if b['date'] < sell['date']:
                buy = b
                break
        
        if buy:
            profit = sell['total_proceeds'] - buy['total_cost']
            if profit > 0:
                winning_trades += 1
                total_profit += profit
            else:
                losing_trades += 1
                total_loss += abs(profit)
    
    win_rate = (winning_trades / len(sell_trades) * 100) if sell_trades else 0
    
    # Daily returns
    daily_values_df = pd.DataFrame(portfolio.daily_values)
    returns = daily_values_df['return_pct'].values
    
    max_return = max(returns)
    min_return = min(returns)
    
    # Maximum drawdown
    peak = daily_values_df['total_value'].cummax()
    drawdown = (daily_values_df['total_value'] - peak) / peak * 100
    max_drawdown = drawdown.min()
    
    # Print summary
    print(f"\n📊 SUMMARY STATISTICS:")
    print("-" * 100)
    print(f"Initial Capital:        ${INITIAL_CAPITAL:,.2f}")
    print(f"Final Value:            ${final_value:,.2f}")
    print(f"Total Return:           ${total_return:,.2f} ({total_return_pct:+.2f}%)")
    print(f"Max Return:             {max_return:+.2f}%")
    print(f"Max Drawdown:           {max_drawdown:.2f}%")
    print()
    print(f"Total Trades:           {num_trades}")
    print(f"Buy Orders:             {len(buy_trades)}")
    print(f"Sell Orders:            {len(sell_trades)}")
    print(f"Winning Trades:         {winning_trades}")
    print(f"Losing Trades:          {losing_trades}")
    print(f"Win Rate:               {win_rate:.1f}%")
    
    if winning_trades > 0:
        avg_win = total_profit / winning_trades
        print(f"Average Win:            ${avg_win:.2f}")
    if losing_trades > 0:
        avg_loss = total_loss / losing_trades
        print(f"Average Loss:           ${avg_loss:.2f}")
    
    print()
    print(f"Final Position:")
    print(f"  Cash:                 ${portfolio.cash:.2f}")
    print(f"  Shares Held:          {portfolio.shares}")
    print(f"  Stock Value:          ${portfolio.shares * portfolio.daily_values[-1]['price']:.2f}")
    
    # Benchmark comparison (buy and hold)
    first_price = portfolio.daily_values[0]['price']
    last_price = portfolio.daily_values[-1]['price']
    buy_hold_shares = int(INITIAL_CAPITAL / first_price)
    buy_hold_value = buy_hold_shares * last_price
    buy_hold_return = ((buy_hold_value - INITIAL_CAPITAL) / INITIAL_CAPITAL) * 100
    
    print()
    print(f"📈 BENCHMARK (Buy & Hold):")
    print("-" * 100)
    print(f"Strategy:               Buy {buy_hold_shares} shares at ${first_price:.2f} and hold")
    print(f"Final Value:            ${buy_hold_value:.2f}")
    print(f"Return:                 {buy_hold_return:+.2f}%")
    print()
    print(f"Strategy vs Benchmark:  {total_return_pct - buy_hold_return:+.2f}% {'✅ OUTPERFORM' if total_return_pct > buy_hold_return else '❌ UNDERPERFORM'}")
    
    # Print transaction log
    print()
    print(f"📋 TRANSACTION LOG:")
    print("-" * 100)
    for t in portfolio.transactions:
        if t['action'] == 'BUY':
            print(f"{t['date']} | BUY  | {t['shares']:4d} shares @ ${t['price']:6.2f} | Cost: ${t['total_cost']:8.2f} | Signal: {t['signal']}")
            print(f"           💡 {t['reason']}")
        else:
            print(f"{t['date']} | SELL | {t['shares']:4d} shares @ ${t['price']:6.2f} | Proceeds: ${t['total_proceeds']:8.2f} | Signal: {t['signal']}")
            print(f"           💡 {t['reason']}")
        print()
    
    # Save detailed results
    save_results(portfolio, {
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'win_rate': win_rate,
        'max_drawdown': max_drawdown,
        'num_trades': num_trades,
        'buy_hold_return': buy_hold_return,
        'outperformance': total_return_pct - buy_hold_return
    })

def save_results(portfolio, metrics):
    """Save results to files"""
    
    # Save transactions
    trans_file = Path(__file__).parent / "backtest_transactions.json"
    with open(trans_file, 'w') as f:
        json.dump(portfolio.transactions, f, indent=2)
    
    # Save daily values
    values_file = Path(__file__).parent / "backtest_daily_values.json"
    with open(values_file, 'w') as f:
        json.dump(portfolio.daily_values, f, indent=2)
    
    # Save metrics
    metrics_file = Path(__file__).parent / "backtest_metrics.json"
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print()
    print("=" * 100)
    print("✅ Results saved:")
    print(f"   📁 {trans_file}")
    print(f"   📁 {values_file}")
    print(f"   📁 {metrics_file}")
    print("=" * 100)

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    try:
        # Load signal data
        signals_file = Path(__file__).parent / "backtest_results.json"
        
        if not signals_file.exists():
            print("❌ Error: backtest_results.json not found")
            print("Please run 'backtest_signals.py' first to generate signals")
            exit(1)
        
        with open(signals_file, 'r') as f:
            signals_data = json.load(f)
        
        print(f"✅ Loaded {len(signals_data)} daily signals from {signals_file}\n")
        
        # Execute trading strategy
        portfolio = execute_strategy(signals_data)
        
        # Analyze performance
        analyze_performance(portfolio)
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
