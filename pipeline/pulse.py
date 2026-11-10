"""Market pulse: the layer that can override the score.

Three questions, answered from data:
  1. What mood is the whole market in?  (regime: Calm / Nervous / Risk-off /
     Panic / Recovering) from S&P 500 trend, the fear gauge (VIXY), and the
     tone of market-wide news.
  2. What is the news talking about?  (themes such as elections, the Fed,
     tariffs, AI spending) and is each theme heating up, and is it positive
     or negative?
  3. For a stock that dropped: was it the market, its sector, or the company?
     A strong company dragged down by the market is a buying opportunity; a
     company-specific drop is a warning. Plus: is it still falling or
     stabilizing, and what happened after similar drops in the past?
"""
import math
import re
from datetime import date, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from . import config
from .build import PRICES_DAILY, connect
from .endpoints import PULSE_ETFS

MARKET_TOPICS = ["financial_markets", "economy_macro", "economy_monetary", "economy_fiscal"]
SECTOR_ETFS = [s for s in PULSE_ETFS if s not in ("SPY", "QQQ", "IWM", "VIXY")]

THEMES = {
    "Elections / politics": ["election", "midterm", "democrat", "republican", "congress", "senate",
                             "white house", "ballot", "vote ", "voters", "campaign"],
    "Fed / interest rates": ["federal reserve", "the fed", "fed's", "rate cut", "rate hike", "powell",
                             "interest rate", "fomc", "treasury yield"],
    "Inflation": ["inflation", "consumer price", " cpi", "price pressures"],
    "Tariffs / trade": ["tariff", "trade war", "export control", "trade deal", "import duties"],
    "AI spending / AI bubble": ["ai bubble", "ai spending", "ai capex", "data center", "artificial intelligence",
                                "ai stocks", "ai trade", "hyperscaler"],
    "Recession / jobs": ["recession", "layoff", "unemployment", "jobs report", "payrolls", "jobless"],
    "Geopolitics / war": [" war ", "missile", "sanction", "invasion", "military", "geopolitic", "ceasefire"],
    "Government shutdown / debt": ["shutdown", "debt ceiling", "deficit", "government funding"],
    "Earnings": ["earnings", "guidance", "quarterly results", "revenue forecast"],
    "Crypto": ["bitcoin", "crypto", "ethereum"],
    "Oil / energy": ["oil price", "crude", "opec", "natural gas"],
}


def load_close(sym: str) -> Optional[pd.Series]:
    p = PRICES_DAILY / f"{sym}.parquet"
    if not p.exists():
        return None
    s = pd.read_parquet(p)["adj_close"].dropna()
    return s[s > 0]


# ------------------------------------------------------------ 1. market regime

def _market_tone(conn) -> Optional[pd.Series]:
    """Daily market-wide news tone: article-weighted mean across market topics."""
    try:
        df = pd.read_sql_query(
            "SELECT date, topic, articles, avg_score FROM market_news_daily WHERE topic IN (%s)"
            % ",".join("?" * len(MARKET_TOPICS)), conn, params=MARKET_TOPICS, parse_dates=["date"])
    except Exception:
        return None
    if df.empty:
        return None
    df["w"] = df["articles"] * df["avg_score"]
    g = df.groupby("date")[["w", "articles"]].sum()
    return (g["w"] / g["articles"]).sort_index()


def _topic_tone(conn, topic) -> Optional[pd.Series]:
    try:
        df = pd.read_sql_query("SELECT date, avg_score FROM market_news_daily WHERE topic=?",
                               conn, params=(topic,), parse_dates=["date"])
    except Exception:
        return None
    return None if df.empty else df.set_index("date")["avg_score"].sort_index()


def _zscore_recent(series: pd.Series, recent_days=7, base_days=90) -> Optional[float]:
    if series is None or len(series) < 30:
        return None
    end = series.index.max()
    recent = series[series.index > end - pd.Timedelta(days=recent_days)]
    base = series[(series.index <= end - pd.Timedelta(days=recent_days))
                  & (series.index > end - pd.Timedelta(days=recent_days + base_days))]
    if len(base) < 20 or base.std() == 0:
        return None
    return float((recent.mean() - base.mean()) / base.std())


def regime_series(conn) -> Optional[pd.DataFrame]:
    """Daily stress points and regime label, so we can also see how the mood moved."""
    spy = load_close("SPY")
    if spy is None or len(spy) < 260:
        return None
    df = pd.DataFrame({"spy": spy})
    df["high"] = df["spy"].rolling(252, min_periods=60).max()
    df["dd"] = df["spy"] / df["high"] - 1
    df["sma20"] = df["spy"].rolling(20).mean()
    df["sma200"] = df["spy"].rolling(200).mean()
    df["r5"] = df["spy"] / df["spy"].shift(5) - 1
    vixy = load_close("VIXY")
    df["vix_spike"] = (vixy / vixy.rolling(20).mean()).reindex(df.index) if vixy is not None else np.nan
    tone = _market_tone(conn)
    if tone is not None and len(tone) >= 30:
        t = tone.reindex(pd.date_range(tone.index.min(), df.index.max())).ffill()
        m7 = t.rolling(7, min_periods=4).mean()
        base = t.shift(7).rolling(90, min_periods=20)
        df["news_z"] = ((m7 - base.mean()) / base.std()).reindex(df.index)
    else:
        df["news_z"] = np.nan

    pts = pd.Series(0, index=df.index, dtype=float)
    pts += np.where(df["dd"] <= -0.10, 2, np.where(df["dd"] <= -0.05, 1, 0))
    pts += np.where(df["r5"] <= -0.04, 1, 0)
    pts += np.where(df["vix_spike"] >= 1.4, 2, np.where(df["vix_spike"] >= 1.2, 1, 0))
    pts += np.where(df["news_z"] <= -2, 2, np.where(df["news_z"] <= -1, 1, 0))
    pts += np.where(df["spy"] < df["sma200"], 1, 0)
    df["stress"] = pts
    label = np.where(pts >= 6, "Panic", np.where(pts >= 3, "Risk-off", np.where(pts >= 2, "Nervous", "Calm")))
    df["regime"] = label
    stressed = pd.Series(np.isin(label, ["Risk-off", "Panic"]), index=df.index)
    recent_stress = stressed.rolling(30, min_periods=1).max().astype(bool)
    recovering = recent_stress & (pts <= 2) & (df["spy"] > df["sma20"])
    df.loc[recovering, "regime"] = "Recovering"
    return df


def market_regime(conn) -> Dict:
    df = regime_series(conn)
    if df is None:
        return {"regime": "unknown", "lines": ["Fetch SPY and VIXY first: python -m pipeline pulse"]}
    last = df.iloc[-1]
    lines = [
        f"S&P 500 (SPY) {last['dd'] * 100:+.1f}% from its 1-year high · last 5 days {last['r5'] * 100:+.1f}% · "
        f"{'above' if last['spy'] > last['sma200'] else 'BELOW'} its 200-day average",
    ]
    if not math.isnan(last["vix_spike"]):
        lines.append(f"Fear gauge (VIXY) {last['vix_spike']:.2f}x its 20-day average "
                     f"({'calm' if last['vix_spike'] < 1.1 else 'elevated' if last['vix_spike'] < 1.4 else 'spiking'})")
    if not math.isnan(last["news_z"]):
        lines.append(f"Market news tone, last 7 days: {last['news_z']:+.1f} standard deviations vs the prior 90 days")
    tech = _zscore_recent(_topic_tone(conn, "technology"))
    if tech is not None:
        lines.append(f"Tech/AI news tone, last 7 days: {tech:+.1f} std vs prior 90 days")
    hist = df["regime"].iloc[-60:]
    changes = hist[hist != hist.shift()]
    path = " → ".join(f"{r} ({d:%b %d})" for d, r in changes.items())
    return {"regime": last["regime"], "stress": int(last["stress"]), "lines": lines,
            "last_60_days": path, "spy_drawdown": float(last["dd"])}


# ------------------------------------------------------------ 2. news themes

def _theme_hits(text: str) -> List[str]:
    t = f" {text.lower()} "
    return [name for name, words in THEMES.items() if any(w in t for w in words)]


def theme_heat(articles: pd.DataFrame, recent_days=7) -> pd.DataFrame:
    """articles: columns date (Timestamp), text, score. Returns theme table:
    mentions in the recent window, share vs normal share ('heat'), and tone."""
    if articles is None or articles.empty:
        return pd.DataFrame()
    end = articles["date"].max()
    articles = articles.assign(themes=articles["text"].map(_theme_hits),
                               recent=articles["date"] > end - pd.Timedelta(days=recent_days))
    rec, old = articles[articles["recent"]], articles[~articles["recent"]]
    rows = []
    for name in THEMES:
        r = rec[rec["themes"].map(lambda ts: name in ts)]
        o = old[old["themes"].map(lambda ts: name in ts)]
        if len(r) < 10:
            continue
        share_r = len(r) / max(len(rec), 1)
        share_o = len(o) / max(len(old), 1)
        rows.append({"theme": name, "articles_7d": len(r), "share_7d": share_r,
                     "heat": share_r / share_o if share_o else float("inf"),
                     "tone_7d": r["score"].mean(), "tone_before": o["score"].mean() if len(o) else np.nan})
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values(["heat", "articles_7d"], ascending=False)


def market_articles(conn, days=67) -> Optional[pd.DataFrame]:
    since = (date.today() - timedelta(days=days)).isoformat()
    try:
        df = pd.read_sql_query("SELECT date, title || ' ' || summary AS text, score FROM market_news_articles "
                               "WHERE date>=?", conn, params=(since,), parse_dates=["date"])
    except Exception:
        return None
    return df


def ticker_articles(sym: str, days=67) -> Optional[pd.DataFrame]:
    from .store import read_json
    folder = config.RAW_DIR / "news_sentiment" / sym
    if not folder.exists():
        return None
    since = (date.today() - timedelta(days=days)).strftime("%Y%m%d")
    rows = []
    for f in sorted(folder.glob("*.json*"))[-3:]:              # the last ~3 monthly files
        for a in read_json(f).get("feed", []):
            if a.get("time_published", "") < since:
                continue
            ts = next((t for t in a.get("ticker_sentiment", []) if t.get("ticker") == sym), None)
            if not ts:
                continue
            rows.append({"date": pd.Timestamp(a["time_published"][:8]),
                         "text": f"{a.get('title', '')} {a.get('summary', '')}",
                         "score": float(ts.get("ticker_sentiment_score") or 0)})
    return pd.DataFrame(rows) if rows else None


# ------------------------------------------------------------ 3. dip analysis

def _log_ret(s):
    return np.log(s).diff()


INDUSTRY_ETF = [("semiconductor", "SMH"), ("software", "IGV"), ("bank", "XLF"), ("insurance", "XLF"),
                ("oil", "XLE"), ("drug", "XLV"), ("biotech", "XLV"), ("medical", "XLV"), ("reit", "XLRE")]
SECTOR_ETF = {"TECHNOLOGY": "XLK", "FINANCIAL SERVICES": "XLF", "ENERGY": "XLE", "HEALTHCARE": "XLV",
              "CONSUMER CYCLICAL": "XLY", "CONSUMER DEFENSIVE": "XLP", "INDUSTRIALS": "XLI",
              "UTILITIES": "XLU", "REAL ESTATE": "XLRE", "BASIC MATERIALS": "XLB",
              "COMMUNICATION SERVICES": "XLC"}


def etf_for_company(conn, sym: str) -> Optional[str]:
    """Match by the company's own industry first (most specific fund). Correlation
    alone misleads for giants: NVDA is ~15% of XLK, so XLK 'moves with' NVDA."""
    try:
        row = conn.execute("SELECT Sector, Industry FROM company WHERE symbol=?", (sym,)).fetchone()
    except Exception:
        return None
    if not row:
        return None
    sector, industry = (row[0] or "").upper(), (row[1] or "").lower()
    for word, etf in INDUSTRY_ETF:
        if word in industry and load_close(etf) is not None:
            return etf
    etf = SECTOR_ETF.get(sector)
    return etf if etf and load_close(etf) is not None else None


def pick_sector_etf(sym_close: pd.Series, spy: pd.Series) -> Optional[str]:
    """Fallback: the sector ETF the stock moves with most, after removing the market."""
    best, best_c = None, 0.2
    rs, rm = _log_ret(sym_close).iloc[-252:], _log_ret(spy)
    for etf in SECTOR_ETFS:
        e = load_close(etf)
        if e is None:
            continue
        df = pd.concat({"s": rs, "m": rm, "e": _log_ret(e)}, axis=1).dropna()
        if len(df) < 120:
            continue
        res_s = df["s"] - np.polyfit(df["m"], df["s"], 1)[0] * df["m"]
        res_e = df["e"] - np.polyfit(df["m"], df["e"], 1)[0] * df["m"]
        c = res_s.corr(res_e)
        if c > best_c:
            best, best_c = etf, c
    return best


def past_drops(close: pd.Series, spy: pd.Series, threshold: float) -> Dict:
    """Every time in history the stock fell `threshold` from its 60-day high
    (one event per 3 months), what happened 3, 6 and 12 months later?
    Also split by whether the market was falling at the same time."""
    df = pd.DataFrame({"p": close, "m": spy}).dropna()
    df["dd"] = df["p"] / df["p"].rolling(60, min_periods=20).max() - 1
    df["mdd"] = df["m"] / df["m"].rolling(60, min_periods=20).max() - 1
    events, skip_until = [], -1
    vals = df["dd"].values
    for i in range(len(df)):
        if i <= skip_until or not vals[i] <= threshold:
            continue
        events.append(i)
        skip_until = i + 63
    out = {"threshold": threshold, "events": []}
    for i in events:
        e = {"date": df.index[i].date().isoformat(), "market_falling": bool(df["mdd"].iloc[i] <= -0.05)}
        for label, h in (("3m", 63), ("6m", 126), ("12m", 252)):
            if i + h < len(df):
                e[label] = float(df["p"].iloc[i + h] / df["p"].iloc[i] - 1)
                e[label + "_spy"] = float(df["m"].iloc[i + h] / df["m"].iloc[i] - 1)
        out["events"].append(e)

    def summary(evts):
        res = {"n": len(evts)}
        for label in ("3m", "6m", "12m"):
            v = [e[label] for e in evts if label in e]
            if v:
                res[label] = {"n": len(v), "up_pct": 100 * sum(x > 0 for x in v) / len(v),
                              "median": float(np.median(v))}
        return res
    out["all"] = summary(out["events"])
    out["market_driven"] = summary([e for e in out["events"] if e["market_falling"]])
    out["company_only"] = summary([e for e in out["events"] if not e["market_falling"]])
    return out


def dip_analysis(sym: str, conn, fund_score=None, est_score=None, has_sell_flag=False,
                 regime: Optional[str] = None) -> Dict:
    close, spy = load_close(sym), load_close("SPY")
    if close is None or spy is None or len(close) < 300:
        return {"status": "no data"}
    recent = close.iloc[-60:]
    peak_date = recent.idxmax()
    peak = recent.max()
    drop = float(close.iloc[-1] / peak - 1)
    out = {"peak_date": peak_date.date().isoformat(), "drop_from_60d_high": drop}
    sector = etf_for_company(conn, sym) or pick_sector_etf(close.loc[:peak_date], spy)
    out["sector_etf"] = sector
    out["sector_name"] = PULSE_ETFS.get(sector) if sector else None

    # Split the move since the peak into market, sector and company parts using
    # the stock's normal sensitivity (beta) measured over the year before the peak.
    sec = load_close(sector) if sector else None
    cols = {"s": _log_ret(close), "m": _log_ret(spy)}
    if sec is not None:
        cols["x"] = _log_ret(sec) - _log_ret(spy)
    df = pd.concat(cols, axis=1).dropna()
    fit = df.loc[:peak_date].iloc[-252:]
    win = df.loc[df.index > peak_date]
    X = np.column_stack([fit[c] for c in cols if c != "s"])
    beta = np.linalg.lstsq(np.column_stack([np.ones(len(fit)), X]), fit["s"], rcond=None)[0][1:]
    tot = win["s"].sum()
    mkt = beta[0] * win["m"].sum()
    sct = beta[1] * win["x"].sum() if sec is not None else 0.0
    idio = tot - mkt - sct
    out.update({"part_market": math.expm1(mkt), "part_sector": math.expm1(sct), "part_company": math.expm1(idio),
                "beta_market": float(beta[0]), "beta_sector": float(beta[1]) if sec is not None else None})

    if drop > -0.08:
        cause = "no meaningful dip"
    elif idio > -0.05 or (tot < 0 and idio / tot < 0.35):
        cause = "market/sector-driven"
    elif idio < -0.08 and tot < 0 and idio / tot > 0.65:
        cause = "company-specific"
    else:
        cause = "mixed"

    # Did the company's own news turn sour during the drop?
    nd = pd.read_sql_query("SELECT date, weighted_score, relevance_sum FROM news_daily WHERE symbol=?",
                           conn, params=(sym,), parse_dates=["date"])
    tone_shift = None
    if not nd.empty:
        nd = nd[nd["relevance_sum"] > 0]
        during = nd[nd["date"] > peak_date]
        before = nd[(nd["date"] <= peak_date) & (nd["date"] > peak_date - pd.Timedelta(days=90))]
        if len(during) >= 3 and len(before) >= 10:
            w = lambda d: (d["weighted_score"] * d["relevance_sum"]).sum() / d["relevance_sum"].sum()
            tone_shift = float(w(during) - w(before))
    out["company_news_shift"] = tone_shift
    if cause in ("mixed", "market/sector-driven") and tone_shift is not None and tone_shift < -0.12:
        cause = "company-specific"   # price says mixed, but the company's own news soured
    out["cause"] = cause

    # Timing: still falling, stabilizing, or recovering?
    sma10, sma20 = close.rolling(10).mean(), close.rolling(20).mean()
    since_peak = close.loc[peak_date:]
    low_date = since_peak.idxmin()
    days_since_low = len(close.loc[low_date:]) - 1
    p = close.iloc[-1]
    if drop > -0.08:
        timing = "n/a"
    elif p < sma10.iloc[-1] or days_since_low < 3:
        timing = "Still falling: wait"
    elif p > sma20.iloc[-1] and sma10.iloc[-1] > sma10.iloc[-6] and regime not in ("Risk-off", "Panic"):
        timing = "Recovering: buy second tranche"
    else:
        timing = "Stabilizing: buy first tranche (1/3)"
    out.update({"low_date": low_date.date().isoformat(), "days_since_low": days_since_low,
                "bounce_from_low": float(p / since_peak.min() - 1), "timing": timing})

    thr = max(min(round(drop, 2), -0.10), -0.40)
    out["history"] = past_drops(close, spy, thr) if drop <= -0.08 else None

    have_sectors = any(load_close(e) is not None for e in SECTOR_ETFS)
    if cause == "company-specific" and not have_sectors and not (tone_shift is not None and tone_shift < -0.12):
        cause = "unclear (sector ETFs not fetched)"
    out["cause"] = cause

    strong = (fund_score or 0) >= 65 and (est_score or 0) >= 55 and not has_sell_flag
    news_ok = tone_shift is None or tone_shift > -0.05
    if drop <= -0.10 and cause.startswith("unclear"):
        action = "REVIEW: can't split sector from company yet; run `pulse --fetch`"
    elif drop <= -0.10 and cause == "company-specific" and strong and news_ok:
        action = "REVIEW: stock-specific drop, but business, estimates and news look fine"
    elif drop <= -0.10 and cause == "company-specific":
        action = "AVOID / REVIEW: the drop is about the company itself"
    elif drop <= -0.10 and cause in ("market/sector-driven", "mixed") and strong:
        action = f"DIP OPPORTUNITY: strong business marked down by the {('market' if abs(mkt) >= abs(sct) else 'sector')}"
    elif drop <= -0.10 and fund_score is None:
        action = "Dip worth checking: run `score` to see if the business is still strong"
    elif drop <= -0.10:
        action = "Dip, but fundamentals are not strong enough to buy it"
    else:
        action = None
    out["action"] = action
    return out


# ------------------------------------------------------------ decision layer

def decide(verdict: str, regime: str, dip: Dict, has_sell_flag: bool) -> str:
    """The final call. Pulse signals override the score when they fire."""
    action = (dip or {}).get("action") or ""
    if action.startswith("AVOID"):
        return "AVOID / REVIEW: company-specific drop"
    if action.startswith("DIP OPPORTUNITY"):
        return f"BUY THE DIP: {dip['timing']}"
    if action.startswith("REVIEW"):
        return "REVIEW before buying: " + action.split(": ", 1)[1]
    if has_sell_flag:
        return "HOLD OFF: sell rule triggered, review first"
    stressed = regime in ("Risk-off", "Panic")
    if verdict == "Strong candidate":
        return "BUY GRADUALLY: market stressed, smaller tranches" if stressed else "BUY: staged 50 / 25 / 25"
    if verdict == "Candidate":
        return "BUY SMALL or wait for a dip" if not stressed else "WATCH: buy only on a deeper dip"
    if verdict.startswith("Watch"):
        return "WATCHLIST: not yet"
    return "AVOID"


# ------------------------------------------------------------ output

def print_market(conn) -> Dict:
    reg = market_regime(conn)
    print("\n" + "═" * 78)
    print(f" MARKET PULSE · {date.today():%b %d, %Y} · regime: {reg['regime'].upper()}"
          + (f" (stress {reg['stress']}/8)" if "stress" in reg else ""))
    print("─" * 78)
    for line in reg["lines"]:
        print(f"  · {line}")
    if reg.get("last_60_days"):
        print(f"  · Last 60 days: {reg['last_60_days']}")
    themes = theme_heat(market_articles(conn))
    if not themes.empty:
        print("\n  What the news is talking about (last 7 days vs before):")
        print(f"  {'Theme':<28}{'Articles':>9}{'Heat':>7}{'Tone now':>10}{'Before':>8}")
        for _, t in themes.head(8).iterrows():
            heat = "new" if math.isinf(t["heat"]) else f"{t['heat']:.1f}x"
            print(f"  {t['theme']:<28}{t['articles_7d']:>9}{heat:>7}{t['tone_7d']:>+10.3f}{t['tone_before']:>+8.3f}")
        print("  (Heat = how much more the theme is discussed than usual. Tone: above +0.15 positive, below -0.15 negative.)")
    sectors = []
    spy = load_close("SPY")
    for etf in SECTOR_ETFS + ["QQQ", "IWM"]:
        c = load_close(etf)
        if c is None or spy is None or len(c) < 25:
            continue
        r20 = c.iloc[-1] / c.iloc[-21] - 1
        s20 = spy.iloc[-1] / spy.iloc[-21] - 1
        sectors.append((etf, PULSE_ETFS[etf], r20, r20 - s20, c.iloc[-1] / c.iloc[-252:].max() - 1))
    if sectors:
        print("\n  Sectors, last 20 trading days:")
        for etf, name, r20, rel, dd in sorted(sectors, key=lambda x: x[3]):
            print(f"  {etf:<5}{name:<28}{r20 * 100:>+7.1f}%  vs S&P {rel * 100:>+6.1f}%   {dd * 100:>+6.1f}% from high")
    return reg


def print_dip(sym: str, d: Dict) -> None:
    if d.get("status") == "no data":
        print(f"\n {sym}: no price data")
        return
    print("\n" + "─" * 78)
    print(f" {sym}: {d['drop_from_60d_high'] * 100:+.1f}% from its 60-day high ({d['peak_date']})"
          f" · sector match: {d['sector_etf'] or 'none'}{' (' + d['sector_name'] + ')' if d['sector_name'] else ''}")
    if d["drop_from_60d_high"] > -0.08:
        print("   No meaningful dip right now.")
        return
    print(f"   Where the drop came from: market {d['part_market'] * 100:+.1f}% · sector {d['part_sector'] * 100:+.1f}%"
          f" · company itself {d['part_company'] * 100:+.1f}%  →  {d['cause'].upper()}")
    if d["company_news_shift"] is not None:
        print(f"   Company news tone during the drop: {d['company_news_shift']:+.3f} vs before")
    print(f"   Low on {d['low_date']} ({d['days_since_low']} trading days ago), bounced {d['bounce_from_low'] * 100:+.1f}% "
          f"since → {d['timing']}")
    h = d.get("history")
    if h:
        def fmt(s):
            parts = [f"{k}: up {v['up_pct']:.0f}% of the time, median {v['median'] * 100:+.0f}%"
                     for k, v in s.items() if k != "n"]
            return f"{s['n']} times; " + "; ".join(parts) if parts else f"{s['n']} times"
        print(f"   History: fell {abs(h['threshold']) * 100:.0f}%+ from a 60-day high {fmt(h['all'])}")
        if h["market_driven"]["n"]:
            print(f"     · when the market was also falling: {fmt(h['market_driven'])}")
        if h["company_only"]["n"]:
            print(f"     · when only the stock fell: {fmt(h['company_only'])}")
    if d.get("action"):
        print(f"   ⇒ {d['action']}")
