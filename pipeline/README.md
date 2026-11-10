# Research pipeline

Downloads Alpha Vantage data into `data_store/`, the local research database. That folder is git-ignored.

## Setup
Add your premium key to `.env` in the repo root:
```
ALPHA_VANTAGE_API_KEY=your_premium_key
```

## Commands
| Command | What it does | Calls |
|---|---|---|
| `python -m pipeline check` | Confirms the key works on premium endpoints | 2 |
| `python -m pipeline market` | Universe list, earnings calendar, macro, BTC/ETH | ~14 |
| `python -m pipeline fetch MSFT NVDA` | Full research set for each stock | ~34 per stock |
| `python -m pipeline fetch SPY QQQ --etf` | Prices and fund profile for benchmarks/ETFs | 3 per ETF |
| `python -m pipeline fetch MSFT --groups prices,forward` | Only some groups | varies |
| `python -m pipeline status [SYMBOL]` | What is stored and what failed | 0 |
| `python -m pipeline build [SYMBOLS]` | Raw files → warehouse tables | 0 |
| `python -m pipeline score MSFT NVDA` | Long-hold scorecard + comparison table (builds first) | 0 |
| `python -m pipeline run MSFT NVDA` | fetch → build → score in one go | ~34 per new stock |

## Stages
1. **Fetch** (`fetch`, `market`): API → `data_store/raw/`
2. **Build** (`build`): raw → `data_store/warehouse/` (SQLite tables + Parquet prices)
3. **Score** (`score`): warehouse → scorecards in `data_store/reports/<date>/` (one JSON per stock + `summary.csv`)

## Long-hold score
| Component | Weight | Built from |
|---|---|---|
| Fundamental | 40% | Existing `FundamentalAnalyzer` (60%) + multi-quarter trends: revenue, margin, free cash flow, buybacks (40%) |
| Estimates | 15% | Next-year EPS estimate change over 90 days, analyst up/down revisions, recent earnings beats |
| Sentiment | 15% | Ticker-specific news tone (90 days, 30-day shift), management tone on earnings calls |
| Trend | 15% | 200-day average, 12-month momentum, return vs SPY |
| Smart money | 15% | Open-market insider buys/sells (codes P/S only), fund buying vs trimming |

Verdicts: ≥70 Strong candidate · ≥60 Candidate · ≥45 Watch · below 45 Avoid. A sell-rule flag caps a candidate at "Watch (red flag)". Risk bucket: Low (<25% volatility, ≥$50B), Medium (≤45%), High.

Options: `--force` (refetch even if fresh), `--workers N` (parallel calls, default 4), `--news-months N` (default 12), `-v` (print every call).

Reruns are cheap: anything still fresh is skipped. Failed calls are always retried on the next run.

## Groups (per stock)
`screen` (OVERVIEW) · `prices` (daily full history and weekly) · `financials` (income, balance sheet, cash flow, earnings, shares, dividends, splits) · `forward` (analyst estimates) · `smart_money` (insiders, institutions) · `sentiment` (12 monthly news windows) · `transcripts` (earnings calls by fiscal quarter) · `etf` · `options`

## Storage layout
```
data_store/
  raw/<endpoint>/<SYMBOL>.json              one file per stock per endpoint
  raw/<endpoint>/<SYMBOL>/<variant>.json    news months, transcript quarters
  raw/global/<endpoint>.json|csv            market-wide data
  catalog.sqlite                            fetch log: status, size and time of every item
  warehouse/                                cleaned tables (next step)
  logs/run_YYYYMMDD.log                     every call, every run
```

To add an endpoint, add one entry to `endpoints.py`.

## Market pulse (can override the score)

```
python -m pipeline pulse --fetch NVDA     # ETF prices + 180 days of market news, then the report
python -m pipeline pulse NVDA MSFT        # report only, from local data
```

- **Regime**: Calm / Nervous / Risk-off / Panic / Recovering, from the S&P 500 drawdown and 200-day average, the VIXY fear gauge, and the tone of market-wide news.
- **Themes**: which subjects (elections, Fed, tariffs, AI spending...) are discussed more than usual this week, and in what tone.
- **Dip check**: splits a stock's drop into market, sector (best-matching sector ETF) and company parts. A strong company pulled down by the market or sector is a **BUY THE DIP** (staged, after it stops falling); a company-specific drop is **AVOID / REVIEW**. Also shows what happened 3/6/12 months after similar past drops.
- `score` prints this as the **DECISION** line at the top of each card, which takes priority over the score.
