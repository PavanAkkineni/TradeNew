"""
COMPARE HIGH RISK vs LOW RISK STRATEGIES
Runs both strategies and provides side-by-side comparison
Initial Capital: $10,000 for both
"""

import json
import subprocess
import sys

def run_strategy(script_name):
    """Run a strategy script and capture output"""
    try:
        result = subprocess.run(
            [sys.executable, script_name],
            capture_output=True,
            text=True,
            cwd='.'
        )
        return result.stdout, result.returncode
    except Exception as e:
        return f"Error running {script_name}: {str(e)}", 1

def load_metrics(filename):
    """Load metrics from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error loading {filename}: {str(e)}")
        return None

def print_comparison():
    """Print side-by-side comparison of both strategies"""
    
    high_risk = load_metrics('high_risk_metrics.json')
    low_risk = load_metrics('low_risk_metrics.json')
    
    if not high_risk or not low_risk:
        print("❌ Error: Could not load metrics files")
        return
    
    print("\n" + "=" * 120)
    print("RISK STRATEGY COMPARISON - $10,000 INITIAL CAPITAL")
    print("=" * 120)
    
    print(f"\n{'METRIC':<30} | {'HIGH RISK':<30} | {'LOW RISK':<30} | {'WINNER':<20}")
    print("-" * 120)
    
    # Returns comparison
    hr_return = high_risk['total_return_pct']
    lr_return = low_risk['total_return_pct']
    winner = "🏆 HIGH RISK" if hr_return > lr_return else "🏆 LOW RISK" if lr_return > hr_return else "🤝 TIE"
    print(f"{'Total Return %':<30} | {hr_return:>28.2f}% | {lr_return:>28.2f}% | {winner:<20}")
    
    hr_dollars = high_risk['total_return']
    lr_dollars = low_risk['total_return']
    print(f"{'Total Return $':<30} | ${hr_dollars:>27.2f} | ${lr_dollars:>27.2f} | ")
    
    # Number of trades
    hr_trades = high_risk['num_trades']
    lr_trades = low_risk['num_trades']
    winner = "📊 HIGH RISK" if hr_trades > lr_trades else "📊 LOW RISK" if lr_trades > hr_trades else "🤝 TIE"
    print(f"{'Number of Trades':<30} | {hr_trades:>30} | {lr_trades:>30} | {winner:<20}")
    
    # Win rate
    hr_winrate = high_risk.get('win_rate', 0)
    lr_winrate = low_risk.get('win_rate', 0)
    if hr_winrate > 0 or lr_winrate > 0:
        winner = "✅ HIGH RISK" if hr_winrate > lr_winrate else "✅ LOW RISK" if lr_winrate > hr_winrate else "🤝 TIE"
        print(f"{'Win Rate':<30} | {hr_winrate:>28.1f}% | {lr_winrate:>28.1f}% | {winner:<20}")
    else:
        print(f"{'Win Rate':<30} | {'N/A':>30} | {'N/A':>30} | ")
    
    # Max drawdown (lower is better)
    hr_dd = high_risk['max_drawdown']
    lr_dd = low_risk['max_drawdown']
    winner = "🛡️ LOW RISK" if abs(lr_dd) < abs(hr_dd) else "🛡️ HIGH RISK" if abs(hr_dd) < abs(lr_dd) else "🤝 TIE"
    print(f"{'Max Drawdown (lower better)':<30} | {hr_dd:>28.2f}% | {lr_dd:>28.2f}% | {winner:<20}")
    
    # Benchmark outperformance
    hr_outperf = high_risk['outperformance']
    lr_outperf = low_risk['outperformance']
    winner = "🎯 HIGH RISK" if hr_outperf > lr_outperf else "🎯 LOW RISK" if lr_outperf > hr_outperf else "🤝 TIE"
    print(f"{'vs Buy-and-Hold':<30} | {hr_outperf:>27.2f}% | {lr_outperf:>27.2f}% | {winner:<20}")
    
    # Buy and hold baseline
    buy_hold = high_risk['buy_hold_return']
    print(f"{'Buy-and-Hold Baseline':<30} | {buy_hold:>28.2f}% | {buy_hold:>28.2f}% | {'📊 BASELINE':<20}")
    
    print("-" * 120)
    
    # Summary
    print(f"\n📊 STRATEGY CHARACTERISTICS:")
    print(f"\n🔴 HIGH RISK:")
    print(f"   • Executes on ALL signals (WEAK_BUY, BUY, STRONG_BUY, WEAK_SELL, SELL, STRONG_SELL)")
    print(f"   • Uses 95% of available cash for positions")
    print(f"   • More trading activity ({hr_trades} trades)")
    print(f"   • Higher potential returns: {hr_return:+.2f}%")
    print(f"   • Higher drawdown risk: {hr_dd:.2f}%")
    
    print(f"\n🟢 LOW RISK:")
    print(f"   • Only executes on STRONG signals (BUY, SELL, STRONG_BUY, STRONG_SELL)")
    print(f"   • Ignores WEAK signals")
    print(f"   • Uses 80% of available cash for positions (20% buffer)")
    print(f"   • Less trading activity ({lr_trades} trades)")
    print(f"   • More conservative returns: {lr_return:+.2f}%")
    print(f"   • Lower drawdown risk: {lr_dd:.2f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    
    if hr_return > lr_return:
        advantage = hr_return - lr_return
        print(f"\n   HIGH RISK strategy outperformed by {advantage:.2f}%")
        if hr_trades > lr_trades * 2:
            print(f"   ⚠️  But required {hr_trades - lr_trades} more trades")
        if abs(hr_dd) > abs(lr_dd) * 1.5:
            print(f"   ⚠️  With {abs(hr_dd) - abs(lr_dd):.2f}% higher max drawdown")
    else:
        advantage = lr_return - hr_return
        print(f"\n   LOW RISK strategy outperformed by {advantage:.2f}%")
        print(f"   ✅ With lower drawdown: {abs(lr_dd):.2f}% vs {abs(hr_dd):.2f}%")
        print(f"   ✅ With fewer trades: {lr_trades} vs {hr_trades}")
    
    print(f"\n   Choose HIGH RISK if:")
    print(f"   • You can tolerate {abs(hr_dd):.2f}% drawdown")
    print(f"   • You want to capture every opportunity")
    print(f"   • You're comfortable with {hr_trades} trades in 1 month")
    
    print(f"\n   Choose LOW RISK if:")
    print(f"   • You prefer {abs(lr_dd):.2f}% max drawdown")
    print(f"   • You want only high-conviction trades")
    print(f"   • You prefer fewer trades ({lr_trades} in 1 month)")
    
    print("\n" + "=" * 120)

def main():
    """Main execution function"""
    
    print("\n" + "=" * 120)
    print("RUNNING RISK STRATEGY COMPARISON")
    print("=" * 120)
    print("\nRunning HIGH RISK strategy...")
    print("-" * 120)
    
    # Run high risk strategy
    output, returncode = run_strategy('analyze_high_risk_strategy.py')
    if returncode != 0:
        print("❌ Error running high risk strategy:")
        print(output)
        return
    print(output)
    
    print("\n" + "=" * 120)
    print("Running LOW RISK strategy...")
    print("-" * 120)
    
    # Run low risk strategy
    output, returncode = run_strategy('analyze_low_risk_strategy.py')
    if returncode != 0:
        print("❌ Error running low risk strategy:")
        print(output)
        return
    print(output)
    
    # Print comparison
    print_comparison()
    
    print("\n✅ COMPARISON COMPLETE!")
    print("\nGenerated files:")
    print("   HIGH RISK: high_risk_transactions.json, high_risk_daily_values.json, high_risk_metrics.json")
    print("   LOW RISK:  low_risk_transactions.json, low_risk_daily_values.json, low_risk_metrics.json")

if __name__ == "__main__":
    main()
