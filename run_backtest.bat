@echo off
echo ================================================================================
echo TRADING SIGNAL BACKTEST - September 3 to October 3, 2025
echo ================================================================================
echo.
echo This script will:
echo   1. Generate trade signals for each day (Sept 3 - Oct 3)
echo   2. Execute trades based on signals with $1000 initial capital
echo   3. Calculate performance and compare to buy-and-hold
echo.
echo Starting backtest...
echo.

echo Step 1: Generating daily trade signals...
echo --------------------------------------------------------------------------------
python backtest_signals.py
echo.

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Signal generation failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Executing trades and analyzing performance...
echo --------------------------------------------------------------------------------
python analyze_backtest_performance.py
echo.

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Performance analysis failed!
    pause
    exit /b 1
)

echo.
echo ================================================================================
echo BACKTEST COMPLETE!
echo ================================================================================
echo.
echo Check the following files for detailed results:
echo   - backtest_results.json       : Daily signals with reasons
echo   - backtest_transactions.json  : Buy/sell transaction log
echo   - backtest_daily_values.json  : Portfolio value tracking
echo   - backtest_metrics.json       : Performance summary
echo.
pause
