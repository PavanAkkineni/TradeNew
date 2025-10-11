@echo off
echo ================================================================================
echo RISK STRATEGY COMPARISON - $10,000 CAPITAL
echo High Risk vs Low Risk Backtesting
echo ================================================================================
echo.

echo Running comparison script...
python compare_risk_strategies.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ================================================================================
    echo SUCCESS! Check the output above for detailed comparison.
    echo ================================================================================
    echo.
    echo Generated files:
    echo   HIGH RISK: high_risk_transactions.json, high_risk_metrics.json
    echo   LOW RISK:  low_risk_transactions.json, low_risk_metrics.json
) else (
    echo ================================================================================
    echo ERROR! Something went wrong. Check the error messages above.
    echo ================================================================================
)

echo.
pause
