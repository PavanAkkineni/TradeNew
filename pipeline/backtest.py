"""Backtest of the dip rules the pulse layer uses, on 20+ years of daily prices.

Question it answers: when a stock falls hard, does it pay to buy?
  · does it matter whether the market / sector caused the fall, or the company?
  · does waiting for the price to stabilize beat buying on the way down?

Every past drop of 15%+ from a 60-day high is an event (at most one per
3 months per stock). Returns are measured 6 and 12 months after the entry,
also relative to the S&P 500 over the same days.

Limits, stated plainly:
  · Survivorship bias: only stocks alive today are tested; companies that
    fell and went bankrupt are missing, so dip buying looks better than it was.
  · Price-only: historical analyst estimates and news tone are not available
    point-in-time, so the "fundamentals still strong" part of the rule cannot
    be tested here. The fundamental scorecard is tested only going forward.
"""
from datetime import date
from typing import List, Optional

import numpy as np
import pandas as pd

from . import config
from .build import PRICES_DAILY, connect
from .pulse import SECTOR_ETFS, etf_for_company, load_close

DROP = -0.15
SPACING = 63            # trading days between events for one stock
HORIZONS = {"6m": 126, "12m": 252}


def _dd(s: pd.Series, window=60) -> pd.Series:
    return s / s.rolling(window, min_periods=20).max() - 1


def events_for(sym: str, conn, spy: pd.Series) -> List[dict]:
    close = load_close(sym)
    if close is None or len(close) < 500:
        return []
    etf = etf_for_company(conn, sym)
    sec = load_close(etf) if etf else None
    df = pd.DataFrame({"p": close, "m": spy}).dropna()
    if sec is not None:
        df["x"] = sec.reindex(df.index)
    df["dd"] = _dd(df["p"])
    df["mdd"] = _dd(df["m"])
    df["xdd"] = _dd(df["x"]) if sec is not None else np.nan
    df["sma10"] = df["p"].rolling(10).mean()
    df["sma20"] = df["p"].rolling(20).mean()
    p, sma10, sma20 = df["p"].values, df["sma10"].values, df["sma20"].values
    out, skip = [], -1
    for i in range(len(df)):
        if i <= skip or not df["dd"].iat[i] <= DROP:
            continue
        skip = i + SPACING
        mdd, xdd = df["mdd"].iat[i], df["xdd"].iat[i]
        if mdd <= -0.07:
            cause = "market falling too"
        elif not np.isnan(xdd) and xdd <= -0.12:
            cause = "sector falling too"
        else:
            cause = "stock alone"
        # entries: same day (catch the knife) vs first day it stabilizes / recovers
        entries = {"buy on the drop": i}
        for j in range(i + 1, min(i + 60, len(df))):
            if "buy when it stabilizes" not in entries and p[j] > sma10[j] and p[j] > p[j - 1]:
                entries["buy when it stabilizes"] = j
            if p[j] > sma20[j] and sma10[j] > sma10[j - 5]:
                entries["buy when it recovers"] = j
                break
        for rule, j in entries.items():
            ev = {"symbol": sym, "date": df.index[i].date(), "cause": cause, "entry": rule,
                  "days_waited": j - i, "entry_vs_drop_day": p[j] / p[i] - 1}
            for h, n in HORIZONS.items():
                if j + n < len(df):
                    r = p[j + n] / p[j] - 1
                    ev[h] = r
                    ev[h + "_vs_spy"] = r - (df["m"].iat[j + n] / df["m"].iat[j] - 1)
            out.append(ev)
    return out


def summarize(ev: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (cause, entry), g in ev.groupby(["cause", "entry"]):
        row = {"cause": cause, "entry": entry, "events": len(g)}
        for h in HORIZONS:
            v = g[h].dropna()
            if len(v):
                row[f"{h} median"] = v.median()
                row[f"{h} up %"] = 100 * (v > 0).mean()
                row[f"{h} vs S&P"] = g[h + "_vs_spy"].dropna().median()
        row["waited (days)"] = g["days_waited"].median()
        rows.append(row)
    return pd.DataFrame(rows)


def run_backtest(symbols: Optional[List[str]] = None) -> pd.DataFrame:
    conn = connect()
    spy = load_close("SPY")
    if spy is None:
        raise SystemExit("Need SPY prices: python -m pipeline fetch SPY --etf")
    skip = set(SECTOR_ETFS) | {"SPY", "QQQ", "IWM", "VIXY", "VOO"}
    if not symbols:
        symbols = sorted(p.stem for p in PRICES_DAILY.glob("*.parquet")
                         if p.stem not in skip and not p.stem.startswith("CRYPTO"))
    all_ev = []
    for s in symbols:
        all_ev += events_for(s, conn, spy)
    conn.close()
    if not all_ev:
        raise SystemExit("No events: fetch more price history first (backtest --fetch N)")
    ev = pd.DataFrame(all_ev)
    tbl = summarize(ev)

    print("\n" + "═" * 92)
    print(f" DIP BACKTEST · {len(symbols)} stocks · {ev['date'].min()} → {ev['date'].max()} · "
          f"{(ev['entry'] == 'buy on the drop').sum()} drops of {abs(DROP) * 100:.0f}%+ from a 60-day high")
    print("─" * 92)
    print(f" {'What else was falling':<22}{'Entry rule':<24}{'Events':>7}{'12m median':>11}{'12m up':>8}"
          f"{'vs S&P':>8}{'6m median':>10}{'wait':>6}")
    order = {"market falling too": 0, "sector falling too": 1, "stock alone": 2}
    for _, r in tbl.sort_values(by=["cause", "entry"], key=lambda c: c.map(order) if c.name == "cause" else c).iterrows():
        f = lambda k, pct=True: (f"{r[k] * 100:+.0f}%" if pct else f"{r[k]:.0f}%") if k in r and pd.notna(r[k]) else "-"
        print(f" {r['cause']:<22}{r['entry']:<24}{r['events']:>7}{f('12m median'):>11}{f('12m up %', False):>8}"
              f"{f('12m vs S&P'):>8}{f('6m median'):>10}{r['waited (days)']:>5.0f}d")
    print("─" * 92)
    print(" Survivorship bias: only today's listed stocks are tested, so results are flattering.\n"
          " Price-only: the 'fundamentals still strong' filter can't be tested on history.")
    out = config.DATA_DIR / "reports" / date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    ev.to_csv(out / "backtest_events.csv", index=False)
    tbl.to_csv(out / "backtest_summary.csv", index=False)
    print(f"\nSaved: {out / 'backtest_summary.csv'} and backtest_events.csv")
    return tbl
