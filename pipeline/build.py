"""Stage 2: turn raw API files into clean, queryable tables.

  warehouse/warehouse.sqlite        company, fundamentals, earnings, estimates,
                                    insider, institutions, news_daily,
                                    transcripts, shares, dividends, macro,
                                    market_news_daily, market_news_articles
  warehouse/prices_daily/<SYM>.parquet
  warehouse/prices_weekly/<SYM>.parquet

Re-running is safe: each symbol's rows are replaced, never duplicated.
"""
import logging
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable, List, Optional

import pandas as pd

from . import config
from .store import find_raw, read_json

log = logging.getLogger("pipeline")

WAREHOUSE_DB = config.WAREHOUSE_DIR / "warehouse.sqlite"
PRICES_DAILY = config.WAREHOUSE_DIR / "prices_daily"
PRICES_WEEKLY = config.WAREHOUSE_DIR / "prices_weekly"


def _num(v) -> Optional[float]:
    if v is None:
        return None
    try:
        s = str(v).strip().rstrip("%")
        if s in ("", "None", "-", "null", "NaN"):
            return None
        return float(s)
    except ValueError:
        return None


def connect() -> sqlite3.Connection:
    config.WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(WAREHOUSE_DB)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def replace_rows(conn, table: str, df: pd.DataFrame, where: dict) -> int:
    """Delete rows matching `where`, then insert df. Creates the table and any
    new columns on the fly, so new API fields never break a build."""
    if df is None or df.empty:
        if conn.execute("SELECT name FROM sqlite_master WHERE name=?", (table,)).fetchone():
            clause = " AND ".join(f'"{k}"=?' for k in where)
            conn.execute(f'DELETE FROM "{table}" WHERE {clause}', tuple(where.values()))
        return 0
    exists = conn.execute("SELECT name FROM sqlite_master WHERE name=?", (table,)).fetchone()
    if not exists:
        df.head(0).to_sql(table, conn, index=False)
        key_cols = ", ".join(f'"{k}"' for k in where)
        conn.execute(f'CREATE INDEX IF NOT EXISTS "ix_{table}" ON "{table}" ({key_cols})')
    else:
        have = {r[1] for r in conn.execute(f'PRAGMA table_info("{table}")')}
        for col in df.columns:
            if col not in have:
                conn.execute(f'ALTER TABLE "{table}" ADD COLUMN "{col}"')
        clause = " AND ".join(f'"{k}"=?' for k in where)
        conn.execute(f'DELETE FROM "{table}" WHERE {clause}', tuple(where.values()))
    df.to_sql(table, conn, index=False, if_exists="append")
    return len(df)


# ---------------- per-symbol builders ----------------

def _load(endpoint, sym, variant=""):
    p = find_raw(endpoint, sym, variant)
    if p is None:
        return None
    try:
        return read_json(p)
    except Exception as e:
        log.warning("could not read %s: %s", p, e)
        return None


def build_prices(sym: str) -> int:
    n = 0
    for endpoint, key_hint, out_dir in (("daily_adjusted", "Daily", PRICES_DAILY),
                                        ("weekly_adjusted", "Weekly", PRICES_WEEKLY)):
        d = _load(endpoint, sym)
        if not d:
            continue
        key = next((k for k in d if key_hint in k and "Series" in k), None)
        if not key:
            continue
        df = pd.DataFrame.from_dict(d[key], orient="index")
        df.columns = [c.split(". ", 1)[-1].replace(" ", "_") for c in df.columns]
        df = df.apply(pd.to_numeric, errors="coerce")
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().rename(columns={"adjusted_close": "adj_close", "dividend_amount": "dividend",
                                             "split_coefficient": "split"})
        df.index.name = "date"
        out_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(out_dir / f"{sym}.parquet")
        n += len(df)
    return n


def build_company(conn, sym: str) -> int:
    d = _load("overview", sym)
    if not d or "Symbol" not in d:
        return replace_rows(conn, "company", None, {"symbol": sym})
    row = {"symbol": sym}
    for k, v in d.items():
        if k == "Symbol":
            continue
        n = _num(v)
        row[k] = v if (n is None or k in ("CIK", "FiscalYearEnd", "LatestQuarter", "DividendDate",
                                           "ExDividendDate")) else n
    return replace_rows(conn, "company", pd.DataFrame([row]), {"symbol": sym})


def build_fundamentals(conn, sym: str) -> int:
    rows = []
    for endpoint, statement in (("income_statement", "income"), ("balance_sheet", "balance"),
                                ("cash_flow", "cash_flow")):
        d = _load(endpoint, sym) or {}
        for period, key in (("annual", "annualReports"), ("quarterly", "quarterlyReports")):
            for rep in d.get(key, []):
                fd = rep.get("fiscalDateEnding")
                for metric, v in rep.items():
                    if metric in ("fiscalDateEnding", "reportedCurrency"):
                        continue
                    val = _num(v)
                    if val is not None:
                        rows.append((sym, statement, period, fd, metric, val))
    df = pd.DataFrame(rows, columns=["symbol", "statement", "period", "fiscal_date", "metric", "value"])
    return replace_rows(conn, "fundamentals", df, {"symbol": sym})


def build_earnings(conn, sym: str) -> int:
    d = _load("earnings", sym) or {}
    rows = [{
        "symbol": sym, "fiscal_date": q.get("fiscalDateEnding"), "reported_date": q.get("reportedDate"),
        "reported_eps": _num(q.get("reportedEPS")), "estimated_eps": _num(q.get("estimatedEPS")),
        "surprise_pct": _num(q.get("surprisePercentage")), "report_time": q.get("reportTime"),
    } for q in d.get("quarterlyEarnings", [])]
    return replace_rows(conn, "earnings", pd.DataFrame(rows), {"symbol": sym})


def build_estimates(conn, sym: str) -> int:
    d = _load("earnings_estimates", sym) or {}
    rows = []
    for e in d.get("estimates", []):
        r = {"symbol": sym, "date": e.get("date"), "horizon": e.get("horizon")}
        for k, v in e.items():
            if k not in ("date", "horizon"):
                r[k] = _num(v)
        rows.append(r)
    return replace_rows(conn, "estimates", pd.DataFrame(rows), {"symbol": sym})


def build_insider(conn, sym: str) -> int:
    d = _load("insider_transactions", sym) or {}
    rows = [{
        "symbol": sym, "date": t.get("transaction_date"), "executive": t.get("executive"),
        "title": t.get("executive_title"), "security_type": t.get("security_type"),
        "code": t.get("acquisition_or_disposal"), "shares": _num(t.get("shares")),
        "price": _num(t.get("share_price")),
    } for t in d.get("data", [])]
    return replace_rows(conn, "insider", pd.DataFrame(rows), {"symbol": sym})


def build_institutions(conn, sym: str) -> int:
    d = _load("institutional_holdings", sym)
    if not d or "holdings" not in d:
        return replace_rows(conn, "institutions", None, {"symbol": sym})
    dates = [h.get("last_reported") for h in d["holdings"] if h.get("last_reported")]
    row = {"symbol": sym, "as_of": max(dates) if dates else None}
    for k, v in d.items():
        if k not in ("symbol", "holdings"):
            row[k] = _num(v)
    return replace_rows(conn, "institutions", pd.DataFrame([row]), {"symbol": sym})


def build_news(conn, sym: str) -> int:
    """Daily aggregate of the sentiment Alpha Vantage assigns *to this ticker*
    in each article, weighted by how relevant the article is to the ticker."""
    folder = config.RAW_DIR / "news_sentiment" / sym
    if not folder.exists():
        return 0
    seen = set()
    agg = defaultdict(lambda: [0, 0.0, 0.0, 0, 0])  # n, sum_score, sum_w*score / weights below
    weights = defaultdict(float)
    for f in sorted(folder.glob("*.json*")):
        try:
            d = read_json(f)
        except Exception as e:
            log.warning("could not read %s: %s", f, e)
            continue
        for a in d.get("feed", []):
            url = a.get("url")
            if url in seen:
                continue
            seen.add(url)
            ts = next((t for t in a.get("ticker_sentiment", []) if t.get("ticker") == sym), None)
            if not ts:
                continue
            score, rel = _num(ts.get("ticker_sentiment_score")), _num(ts.get("relevance_score")) or 0
            if score is None:
                continue
            day = a.get("time_published", "")[:8]
            day = f"{day[:4]}-{day[4:6]}-{day[6:8]}"
            s = agg[day]
            s[0] += 1
            s[1] += score
            s[2] += score * rel
            weights[day] += rel
            s[3] += score >= 0.15
            s[4] += score <= -0.15
    rows = [{
        "symbol": sym, "date": day, "articles": n,
        "avg_score": round(total / n, 4),
        "weighted_score": round(wsum / weights[day], 4) if weights[day] else None,
        "relevance_sum": round(weights[day], 3),
        "bullish": bull, "bearish": bear,
    } for day, (n, total, wsum, bull, bear) in sorted(agg.items())]
    return replace_rows(conn, "news_daily", pd.DataFrame(rows), {"symbol": sym})


def build_transcripts(conn, sym: str) -> int:
    folder = config.RAW_DIR / "earnings_transcript" / sym
    rows = []
    for f in sorted(folder.glob("*.json")) if folder.exists() else []:
        d = read_json(f)
        turns = d.get("transcript") or []
        if not turns:
            continue
        def avg(sel):
            vals = [_num(t.get("sentiment")) for t in turns if sel(t)]
            vals = [v for v in vals if v is not None]
            return round(sum(vals) / len(vals), 4) if vals else None
        is_analyst = lambda t: "analyst" in (t.get("title") or "").lower()
        is_operator = lambda t: (t.get("title") or "").lower() == "operator"
        rows.append({
            "symbol": sym, "quarter": d.get("quarter") or f.stem, "turns": len(turns),
            "avg_sentiment": avg(lambda t: True),
            "management_sentiment": avg(lambda t: not is_analyst(t) and not is_operator(t)),
            "analyst_sentiment": avg(is_analyst),
        })
    return replace_rows(conn, "transcripts", pd.DataFrame(rows), {"symbol": sym})


def build_shares_dividends(conn, sym: str) -> int:
    d = _load("shares_outstanding", sym) or {}
    shares = pd.DataFrame([{
        "symbol": sym, "date": r.get("date"),
        "diluted": _num(r.get("shares_outstanding_diluted")), "basic": _num(r.get("shares_outstanding_basic")),
    } for r in d.get("data", [])])
    d = _load("dividends", sym) or {}
    divs = pd.DataFrame([{"symbol": sym, "ex_date": r.get("ex_dividend_date"), "amount": _num(r.get("amount"))}
                         for r in d.get("data", [])])
    return replace_rows(conn, "shares", shares, {"symbol": sym}) + replace_rows(conn, "dividends", divs, {"symbol": sym})


SYMBOL_BUILDERS = [build_company, build_fundamentals, build_earnings, build_estimates, build_insider,
                   build_institutions, build_news, build_transcripts, build_shares_dividends]


# ---------------- market-wide ----------------

MACRO_SERIES = ["treasury_10y", "treasury_2y", "fed_funds_rate", "cpi", "inflation", "unemployment",
                "nonfarm_payroll", "retail_sales", "real_gdp"]


def build_market(conn) -> int:
    n = 0
    for name in MACRO_SERIES:
        d = _load(name, None)
        if not d:
            continue
        df = pd.DataFrame([{"series": name, "date": r["date"], "value": _num(r["value"])}
                           for r in d.get("data", [])])
        n += replace_rows(conn, "macro", df, {"series": name})
    for name in ("listing_active", "listing_delisted"):
        p = find_raw(name, None)
        if p:
            df = pd.read_csv(p, keep_default_na=False)
            df["list"] = name
            n += replace_rows(conn, "listings", df, {"list": name})
    p = find_raw("earnings_calendar", None)
    if p:
        df = pd.read_csv(p, keep_default_na=False)
        df["calendar"] = "next_12m"
        n += replace_rows(conn, "earnings_calendar", df, {"calendar": "next_12m"})
    for coin in ("btc", "eth"):
        d = _load(f"crypto_{coin}_weekly", None)
        if not d:
            continue
        key = next((k for k in d if "Time Series" in k), None)
        df = pd.DataFrame.from_dict(d[key], orient="index")
        df.columns = [c.split(". ", 1)[-1] for c in df.columns]
        df = df.apply(pd.to_numeric, errors="coerce")
        df.index = pd.to_datetime(df.index)
        df.index.name = "date"
        PRICES_WEEKLY.mkdir(parents=True, exist_ok=True)
        df.sort_index().to_parquet(PRICES_WEEKLY / f"CRYPTO_{coin.upper()}.parquet")
        n += len(df)
    return n


def build_market_news(conn) -> int:
    """Market-wide topic news (the pulse feed): a daily tone per topic, plus the
    last 90 days of headlines so themes (elections, Fed, tariffs...) can be found."""
    from .endpoints import PULSE_TOPICS
    n = 0
    cutoff = (date.today() - timedelta(days=90)).strftime("%Y%m%d")
    articles, seen_all = [], set()
    for topic in PULSE_TOPICS:
        folder = config.RAW_DIR / "global" / f"market_news_{topic}"
        if not folder.exists():
            continue
        seen, agg = set(), defaultdict(lambda: [0, 0.0, 0, 0])
        for f in sorted(folder.glob("*.json*")):
            try:
                d = read_json(f)
            except Exception as e:
                log.warning("could not read %s: %s", f, e)
                continue
            for a in d.get("feed", []):
                url = a.get("url")
                score = _num(a.get("overall_sentiment_score"))
                if url in seen or score is None:
                    continue
                seen.add(url)
                day = a.get("time_published", "")[:8]
                s = agg[day]
                s[0] += 1; s[1] += score; s[2] += score >= 0.15; s[3] += score <= -0.15
                if day >= cutoff and url not in seen_all:
                    seen_all.add(url)
                    articles.append({"topic": topic, "date": f"{day[:4]}-{day[4:6]}-{day[6:8]}",
                                     "title": a.get("title") or "", "summary": a.get("summary") or "",
                                     "source": a.get("source"), "score": score})
        rows = [{"topic": topic, "date": f"{d[:4]}-{d[4:6]}-{d[6:8]}", "articles": v[0],
                 "avg_score": round(v[1] / v[0], 4), "bullish": v[2], "bearish": v[3]}
                for d, v in sorted(agg.items())]
        n += replace_rows(conn, "market_news_daily", pd.DataFrame(rows), {"topic": topic})
    if articles:
        conn.execute("DROP TABLE IF EXISTS market_news_articles")
        pd.DataFrame(articles).to_sql("market_news_articles", conn, index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS ix_mna_date ON market_news_articles(date)")
        n += len(articles)
    return n


def stored_symbols() -> List[str]:
    syms = set()
    for ep_dir in config.RAW_DIR.iterdir() if config.RAW_DIR.exists() else []:
        if not ep_dir.is_dir() or ep_dir.name == "global":
            continue
        for p in ep_dir.iterdir():
            name = p.name.split(".")[0]
            if name:
                syms.add(name)
    return sorted(syms)


def build(symbols: Optional[Iterable[str]] = None) -> dict:
    conn = connect()
    symbols = sorted({s.upper() for s in symbols}) if symbols else stored_symbols()
    summary = {"market_rows": build_market(conn) + build_market_news(conn)}
    conn.commit()
    for sym in symbols:
        counts = {"prices": build_prices(sym)}
        for fn in SYMBOL_BUILDERS:
            try:
                counts[fn.__name__.replace("build_", "")] = fn(conn, sym)
            except Exception as e:
                log.exception("build %s %s failed: %s", fn.__name__, sym, e)
                counts[fn.__name__.replace("build_", "")] = "error"
        conn.commit()
        summary[sym] = counts
    conn.close()
    return summary
