"""Whole-market scan: one cheap call per stock (OVERVIEW), rank everything,
then spend the expensive deep fetch only on the best few hundred.

  stage 1  universe   active US common stocks from LISTING_STATUS (no warrants/units/SPACs)
  stage 2  overview   1 call per stock (~7,800 calls, ~2 hours at 70/min, cached 7 days)
  stage 3  prescore   rank on quality, growth, value, analysts and trend (percentiles)
  stage 4  deep       full fetch + scorecard + pulse decision for the top N
"""
import logging
import re
from datetime import date
from typing import List

import numpy as np
import pandas as pd

from . import config, endpoints
from .build import build_company, connect

log = logging.getLogger("pipeline")

EXCHANGES = ("NYSE", "NASDAQ", "AMEX", "NYSE MKT", "NYSE ARCA")
JUNK = re.compile(r"\b(warrants?|units?|rights?|acquisition corp|acquisition co|blank check|spac|"
                  r"preferred|notes due|depositary shares representing)\b", re.I)
MIN_MCAP = 300e6


def universe(conn) -> List[str]:
    df = pd.read_sql_query("SELECT symbol, name, exchange, assetType FROM listings WHERE list='listing_active'", conn)
    if df.empty:
        raise SystemExit("No listing data. Run: python -m pipeline market --groups universe")
    df = df[(df["assetType"] == "Stock") & df["exchange"].isin(EXCHANGES)
            & df["symbol"].str.fullmatch(r"[A-Z]{1,5}") & ~df["name"].fillna("").str.contains(JUNK)]
    return sorted(df["symbol"].unique())


def _pct_rank(s: pd.Series, higher_is_better=True) -> pd.Series:
    r = s.rank(pct=True, ascending=higher_is_better) * 100
    return r.fillna(50)                       # missing data = middle of the pack


def prescore(conn) -> pd.DataFrame:
    """Rank every stock with an overview on its own fundamentals. This is a
    filter, not a verdict: the deep scorecard decides."""
    df = pd.read_sql_query("SELECT * FROM company", conn)
    for c in df.columns:
        if c not in ("symbol", "Name", "Sector", "Industry", "Exchange", "Country", "AssetType", "Description"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[(df["AssetType"].fillna("Common Stock") == "Common Stock") & (df["MarketCapitalization"] >= MIN_MCAP)].copy()
    price = df["50DayMovingAverage"]
    fpe = df["ForwardPE"].where(df["ForwardPE"] > 0)
    peg = df["PEGRatio"].where(df["PEGRatio"] > 0)
    ratings = df[["AnalystRatingStrongBuy", "AnalystRatingBuy", "AnalystRatingHold",
                  "AnalystRatingSell", "AnalystRatingStrongSell"]].fillna(0)
    n_ratings = ratings.sum(axis=1)
    rating = ((2 * ratings.iloc[:, 0] + ratings.iloc[:, 1] - ratings.iloc[:, 3] - 2 * ratings.iloc[:, 4])
              / n_ratings.replace(0, np.nan))
    df["target_upside"] = df["AnalystTargetPrice"] / price - 1
    df["trend_50_200"] = df["50DayMovingAverage"] / df["200DayMovingAverage"] - 1
    df["range_pos"] = (price - df["52WeekLow"]) / (df["52WeekHigh"] - df["52WeekLow"])
    df["analysts"] = n_ratings

    quality = (_pct_rank(df["ProfitMargin"]) + _pct_rank(df["OperatingMarginTTM"])
               + _pct_rank(df["ReturnOnEquityTTM"].clip(-1, 1))) / 3
    growth = (_pct_rank(df["QuarterlyRevenueGrowthYOY"]) + _pct_rank(df["QuarterlyEarningsGrowthYOY"].clip(-2, 5))) / 2
    value = (_pct_rank(fpe, higher_is_better=False) + _pct_rank(peg, higher_is_better=False)) / 2
    analyst = (_pct_rank(rating) + _pct_rank(df["target_upside"].clip(-0.5, 2))) / 2
    trend = (_pct_rank(df["trend_50_200"]) + _pct_rank(df["range_pos"])) / 2
    df["q"], df["g"], df["v"], df["a"], df["t"] = quality, growth, value, analyst, trend
    df["prescore"] = (0.30 * quality + 0.25 * growth + 0.15 * value + 0.15 * analyst + 0.15 * trend).round(1)
    # Long-hold basics: must make money or be growing fast, and be covered by analysts.
    df["passes"] = ((df["ProfitMargin"] > 0) | (df["QuarterlyRevenueGrowthYOY"] > 0.25)) & (n_ratings >= 3)
    return df.sort_values("prescore", ascending=False)


def run_scan(fetch: bool, workers: int, top: int, deep: int, force: bool = False) -> pd.DataFrame:
    from .fetch import Fetcher, build_tasks
    conn = connect()
    syms = universe(conn)
    print(f"Universe: {len(syms)} US common stocks")
    if fetch:
        tasks = build_tasks(endpoints.symbol_endpoints(["screen"]), syms)
        Fetcher(workers, force).run(tasks)
    built = 0
    for s in syms:
        try:
            built += bool(build_company(conn, s))
        except Exception as e:
            log.warning("overview %s: %s", s, e)
    conn.commit()
    print(f"Overviews in warehouse: {built}")
    df = prescore(conn)
    conn.close()
    good = df[df["passes"]]
    out = config.DATA_DIR / "reports" / date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    cols = ["symbol", "Name", "Sector", "Industry", "MarketCapitalization", "prescore", "q", "g", "v", "a", "t",
            "ForwardPE", "PEGRatio", "QuarterlyRevenueGrowthYOY", "ProfitMargin", "target_upside", "analysts", "passes"]
    df[cols].to_csv(out / "scan.csv", index=False)
    (out / "scan_top.txt").write_text(" ".join(good["symbol"].head(top)), encoding="utf-8")

    print(f"\n{len(df)} stocks ≥ ${MIN_MCAP / 1e6:.0f}M market cap · {len(good)} pass the basics "
          f"(profitable or fast-growing, ≥3 analysts)\n")
    print(f" {'#':>3} {'Symbol':<7}{'Pre':>5} {'Qual':>5}{'Grow':>5}{'Val':>5}{'Anl':>5}{'Trnd':>5}  "
          f"{'Cap $B':>8}  {'Sector':<22}Name")
    for i, (_, r) in enumerate(good.head(top).iterrows(), 1):
        print(f" {i:>3} {r['symbol']:<7}{r['prescore']:>5.0f} {r['q']:>5.0f}{r['g']:>5.0f}{r['v']:>5.0f}{r['a']:>5.0f}"
              f"{r['t']:>5.0f}  {r['MarketCapitalization'] / 1e9:>8.1f}  {str(r['Sector'] or '')[:21]:<22}"
              f"{str(r['Name'])[:30]}")
    sectors = good.head(top)["Sector"].value_counts()
    print("\n Sector mix of the top list: " + ", ".join(f"{k.title()} {v}" for k, v in sectors.items()))
    print(f"\nSaved: {out / 'scan.csv'}  (all stocks) and scan_top.txt (top {top})")
    if deep:
        picks = list(good["symbol"].head(deep))
        print(f"\nDeep fetch for the top {deep} (~40 calls each, ~{deep * 40 / 70:.0f} min):")
        tasks = build_tasks(endpoints.symbol_endpoints(endpoints.DEFAULT_STOCK_GROUPS), picks)
        Fetcher(workers, force).run(tasks)
    return good
