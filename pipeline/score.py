"""Stage 3: long-hold scorecard for a stock.

Five components, each scored 0-100 (50 = neutral), combined with long-hold
weights. The existing app logic is reused where it fits:
  - FundamentalAnalyzer (app/fundamental_analysis.py) is the core of the
    fundamental score, extended with multi-quarter trends.
  - TechnicalAnalyzer's RSI is reported for context; the trend score itself
    uses long-horizon measures (200-day average, 12-month momentum).

Red flags implement the sell rules from the plan. They don't change the score;
they are reported separately so a strong score with a flag still gets a look.
"""
import json
import math
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd

from app.fundamental_analysis import FundamentalAnalyzer
from app.technical_analysis import TechnicalAnalyzer

from . import config
from .build import PRICES_DAILY, _load, connect

WEIGHTS = {"fundamental": 0.40, "estimates": 0.15, "sentiment": 0.15, "trend": 0.15, "smart_money": 0.15}
REPORT_DIR = config.DATA_DIR / "reports"


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def _pct(x, digits=1):
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(x * 100, digits)


class Card:
    """Collects one component's score and the plain-language reasons for it."""

    def __init__(self, name):
        self.name, self.score, self.facts, self.flags = name, None, [], []

    def fact(self, text):
        self.facts.append(text)

    def flag(self, severity, text):
        self.flags.append({"severity": severity, "text": text})

    def as_dict(self):
        return {"score": None if self.score is None else round(self.score, 1),
                "facts": self.facts, "flags": self.flags}


# ---------------------------------------------------------------- fundamental

def _quarterly(conn, sym, statement, metrics) -> pd.DataFrame:
    q = pd.read_sql_query(
        "SELECT fiscal_date, metric, value FROM fundamentals WHERE symbol=? AND statement=? "
        "AND period='quarterly' AND metric IN (%s)" % ",".join("?" * len(metrics)),
        conn, params=(sym, statement, *metrics))
    if q.empty:
        return q
    return q.pivot_table(index="fiscal_date", columns="metric", values="value").sort_index(ascending=False)


def score_fundamental(conn, sym) -> Card:
    c = Card("fundamental")
    raw = {k: _load(ep, sym) or {} for k, ep in (("overview", "overview"), ("income", "income_statement"),
                                                  ("balance", "balance_sheet"), ("cash_flow", "cash_flow"),
                                                  ("earnings", "earnings"))}
    if not raw["overview"] and not raw["income"]:
        return c
    base = FundamentalAnalyzer().analyze(raw)
    base_score = base["scores"]["overall"]
    s = base["scores"]
    c.fact(f"Existing fundamental model: {base_score:.0f}/100 (valuation {s['valuation']:.0f}, "
           f"profitability {s['profitability']:.0f}, growth {s['growth']:.0f}, health {s['health']:.0f})")

    trend = 50.0
    inc = _quarterly(conn, sym, "income", ["totalRevenue", "operatingIncome"])
    cf = _quarterly(conn, sym, "cash_flow", ["operatingCashflow", "capitalExpenditures"])
    if len(inc) >= 8 and "totalRevenue" in inc:
        rev = inc["totalRevenue"]
        rev_ttm, rev_prev = rev.iloc[:4].sum(), rev.iloc[4:8].sum()
        g = rev_ttm / rev_prev - 1 if rev_prev else None
        if g is not None:
            trend += 20 if g > 0.20 else 10 if g > 0.10 else 0 if g >= 0 else -20
            c.fact(f"Revenue last 12 months: {g * 100:+.1f}% vs the 12 months before")
        if "operatingIncome" in inc:
            opm_now = inc["operatingIncome"].iloc[:4].sum() / rev_ttm if rev_ttm else None
            opm_prev = inc["operatingIncome"].iloc[4:8].sum() / rev_prev if rev_prev else None
            if opm_now is not None and opm_prev is not None:
                d = opm_now - opm_prev
                trend += 10 if d > 0.02 else -10 if d < -0.02 else 0
                c.fact(f"Operating margin {opm_now * 100:.1f}% ({d * 100:+.1f} pts vs prior year)")
        yoy = [rev.iloc[i] / rev.iloc[i + 4] - 1 for i in range(2) if rev.iloc[i + 4]]
        if len(yoy) == 2 and all(x < 0 for x in yoy):
            c.flag("sell", "Revenue fell year-over-year in each of the last 2 quarters")
    if len(cf) >= 4 and "operatingCashflow" in cf:
        ocf = cf["operatingCashflow"].iloc[:4].sum()
        capex = abs(cf.get("capitalExpenditures", pd.Series([0] * 4)).iloc[:4].sum())
        rev_ttm = inc["totalRevenue"].iloc[:4].sum() if len(inc) >= 4 else None
        fcf = ocf - capex
        if rev_ttm:
            m = fcf / rev_ttm
            trend += 10 if m > 0.15 else 0 if m >= 0 else -15
            c.fact(f"Free cash flow margin {m * 100:.1f}% (cash left after investment, per $ of sales)")
    sh = pd.read_sql_query("SELECT date, diluted FROM shares WHERE symbol=? ORDER BY date DESC", conn, params=(sym,))
    if len(sh) >= 5 and sh["diluted"].iloc[4]:
        ch = sh["diluted"].iloc[0] / sh["diluted"].iloc[4] - 1
        trend += 5 if ch < -0.01 else -10 if ch > 0.03 else 0
        c.fact(f"Share count {ch * 100:+.1f}% over a year ({'buybacks' if ch < 0 else 'dilution' if ch > 0.005 else 'flat'})")
    trend = clamp(trend, 0, 100)
    c.score = 0.6 * base_score + 0.4 * trend
    c.fact(f"Multi-quarter trend score: {trend:.0f}/100")
    return c


# ---------------------------------------------------------------- estimates

def score_estimates(conn, sym) -> Card:
    c = Card("estimates")
    cutoff = (date.today() + timedelta(days=120)).isoformat()
    row = conn.execute(
        "SELECT * FROM estimates WHERE symbol=? AND horizon='fiscal year' AND date>? ORDER BY date LIMIT 1",
        (sym, cutoff)).fetchone()
    score = 50.0
    if row:
        cols = [d[0] for d in conn.execute("SELECT * FROM estimates LIMIT 0").description]
        e = dict(zip(cols, row))
        avg, a30, a60, a90 = (e.get(k) for k in ("eps_estimate_average", "eps_estimate_average_30_days_ago",
                                                  "eps_estimate_average_60_days_ago", "eps_estimate_average_90_days_ago"))
        def chg(old):
            return (avg - old) / abs(old) if avg is not None and old else None
        c90, c60 = chg(a90), chg(a60)
        if c90 is not None:
            score += clamp(c90 * 150, -30, 30)
            c.fact(f"Fiscal year ending {e['date']}: EPS estimate ${avg:.2f}, {c90 * 100:+.1f}% vs 90 days ago "
                   f"({int(e.get('eps_estimate_analyst_count') or 0)} analysts)")
        if c60 is not None and c60 < -0.10:
            c.flag("sell", f"Analysts cut next-year EPS estimate {c60 * 100:.0f}% in 60 days")
        up, down = e.get("eps_estimate_revision_up_trailing_30_days") or 0, e.get("eps_estimate_revision_down_trailing_30_days") or 0
        if up + down:
            score += 15 * (up - down) / (up + down)
            c.fact(f"Last 30 days: {int(up)} analysts raised, {int(down)} lowered")
    beats = conn.execute(
        "SELECT surprise_pct FROM earnings WHERE symbol=? AND surprise_pct IS NOT NULL "
        "ORDER BY fiscal_date DESC LIMIT 4", (sym,)).fetchall()
    if beats:
        n = sum(1 for (s,) in beats if s > 0)
        score += (n - 2) * 4
        c.fact(f"Beat earnings estimates in {n} of last {len(beats)} quarters")
    if row or beats:
        c.score = clamp(score, 0, 100)
    return c


# ---------------------------------------------------------------- sentiment

def score_sentiment(conn, sym) -> Card:
    c = Card("sentiment")
    nd = pd.read_sql_query("SELECT date, articles, weighted_score, relevance_sum FROM news_daily WHERE symbol=?",
                           conn, params=(sym,), parse_dates=["date"])
    score = 50.0
    have = False
    if not nd.empty:
        today = pd.Timestamp(date.today())
        def window(lo, hi):
            w = nd[(nd["date"] > today - pd.Timedelta(days=hi)) & (nd["date"] <= today - pd.Timedelta(days=lo))]
            w = w[w["relevance_sum"] > 0]
            if w.empty:
                return None, 0
            return (w["weighted_score"] * w["relevance_sum"]).sum() / w["relevance_sum"].sum(), int(w["articles"].sum())
        s30, n30 = window(0, 30)
        s90, n90 = window(0, 90)
        base, nbase = window(90, 270)
        if s90 is not None:
            have = True
            score += clamp((s90 - 0.10) * 120, -20, 20)
            mood = "bullish" if s90 >= 0.35 else "somewhat bullish" if s90 >= 0.15 else "neutral" if s90 > -0.15 else "bearish"
            c.fact(f"News tone last 90 days: {s90:+.3f} ({mood}; {n90} articles)")
        if s30 is not None and base is not None:
            score += clamp((s30 - base) * 150, -15, 15)
            c.fact(f"Last 30 days {s30:+.3f} vs earlier baseline {base:+.3f}")
            daily_rate_base = nbase / 180 if nbase else 0
            spike = (n30 / 30) / daily_rate_base if daily_rate_base else 1
            if s30 < base - 0.10 and spike > 1.5:
                c.flag("review", f"News turning negative on {spike:.1f}x normal volume")
        coverage = nd["date"].dt.to_period("M").nunique()
        if coverage < 10:
            c.fact(f"Note: news covers only {coverage} months; refetch with paging for full history")
    tr = conn.execute("SELECT quarter, management_sentiment FROM transcripts WHERE symbol=? "
                      "AND management_sentiment IS NOT NULL ORDER BY quarter DESC LIMIT 4", (sym,)).fetchall()
    if len(tr) >= 2:
        have = True
        latest, prev = tr[0][1], sum(t[1] for t in tr[1:]) / (len(tr) - 1)
        score += clamp((latest - prev) * 50, -10, 10)
        c.fact(f"Management tone on {tr[0][0]} call: {latest:.2f} vs {prev:.2f} average of prior calls")
    if have:
        c.score = clamp(score, 0, 100)
    return c


# ---------------------------------------------------------------- trend

def _prices(sym) -> Optional[pd.DataFrame]:
    p = PRICES_DAILY / f"{sym}.parquet"
    return pd.read_parquet(p) if p.exists() else None


def _ret_12m(df) -> Optional[float]:
    s = df["adj_close"].dropna()
    return s.iloc[-1] / s.iloc[-253] - 1 if len(s) > 253 else None


def score_trend(sym, benchmark="SPY") -> (Card, dict):
    c = Card("trend")
    df = _prices(sym)
    stats = {}
    if df is None or len(df) < 260:
        return c, stats
    adj = df["adj_close"].dropna()
    price = float(df["close"].iloc[-1])
    sma200 = adj.rolling(200).mean()
    above = adj.iloc[-1] > sma200.iloc[-1]
    rising = sma200.iloc[-1] > sma200.iloc[-21]
    mom = adj.iloc[-22] / adj.iloc[-253] - 1
    r12 = _ret_12m(df)
    high = adj.iloc[-252:].max()
    dd = adj.iloc[-1] / high - 1
    vol = adj.pct_change().iloc[-252:].std() * math.sqrt(252)
    stats = {"price": price, "ret_12m": r12, "drawdown": dd, "volatility": vol}

    score = 50 + (15 if above else -15) + (10 if rising else -10) + clamp(mom * 50, -15, 15)
    c.fact(f"Price {'above' if above else 'below'} its 200-day average, which is {'rising' if rising else 'falling'}")
    c.fact(f"12-month return {r12 * 100:+.1f}%; momentum excluding last month {mom * 100:+.1f}%")
    bench = _prices(benchmark)
    if bench is not None and sym != benchmark:
        b12 = _ret_12m(bench)
        if b12 is not None:
            score += clamp((r12 - b12) * 30, -10, 10)
            c.fact(f"{benchmark} 12-month return {b12 * 100:+.1f}% -> {'beating' if r12 > b12 else 'lagging'} the market")
    else:
        c.fact(f"(fetch {benchmark} with --etf to compare against the market)")
    c.fact(f"{dd * 100:.0f}% from its 52-week high · volatility {vol * 100:.0f}%/yr")
    try:
        rsi = TechnicalAnalyzer().calculate_rsi(df)
        c.fact(f"RSI(14) {rsi:.0f} (short-term; context only, not scored)")
    except Exception:
        pass
    if not above and not rising:
        c.flag("watch", "Below a falling 200-day average (sell only if another flag appears)")
    stats["trend_break"] = (not above and not rising)
    c.score = clamp(score, 0, 100)
    return c, stats


# ---------------------------------------------------------------- smart money

def score_smart_money(conn, sym, market_cap) -> Card:
    c = Card("smart_money")
    score, have = 50.0, False
    since = (date.today() - timedelta(days=180)).isoformat()
    ins = pd.read_sql_query("SELECT date, executive, code, shares, price FROM insider "
                            "WHERE symbol=? AND date>=? AND code IN ('P','S')", conn, params=(sym, since))
    if not ins.empty or conn.execute("SELECT 1 FROM insider WHERE symbol=? LIMIT 1", (sym,)).fetchone():
        have = True
        ins["value"] = ins["shares"].fillna(0) * ins["price"].fillna(0)
        buys, sells = ins[ins["code"] == "P"], ins[ins["code"] == "S"]
        buyers = buys["executive"].nunique()
        score += 20 if buyers >= 2 else 10 if buyers == 1 else 0
        sell_val = sells["value"].sum()
        if market_cap:
            pct = sell_val / market_cap * 100
            score -= 15 if pct > 0.5 else 5 if pct > 0.1 else 0
        c.fact(f"Insiders, 6 months (open market only): {buyers} buyer(s) ${buys['value'].sum() / 1e6:,.1f}M · "
               f"{sells['executive'].nunique()} seller(s) ${sell_val / 1e6:,.1f}M")
        recent = sells[sells["date"] >= (date.today() - timedelta(days=30)).isoformat()]
        if recent["executive"].nunique() >= 3:
            c.flag("review", f"{recent['executive'].nunique()} insiders sold in the last 30 days")
    inst = conn.execute("SELECT holders_with_increased_holdings, holders_with_decreased_holdings, "
                        "shares_with_increased_holdings, shares_with_decreased_holdings, "
                        "total_institutional_shares, total_institutional_ownership_percentage, as_of "
                        "FROM institutions WHERE symbol=?", (sym,)).fetchone()
    if inst and inst[0] is not None:
        have = True
        up, down, sup, sdown, total, own, as_of = inst
        ratio = up / (up + down) if up + down else 0.5
        flow = (sup - sdown) / total if total else 0
        score += clamp((ratio - 0.5) * 100, -15, 15) + clamp(flow * 300, -10, 10)
        c.fact(f"Funds (13F as of {as_of}): {int(up)} added vs {int(down)} trimmed; "
               f"net {flow * 100:+.1f}% of fund-held shares; funds own {own:.0f}%")
    if have:
        c.score = clamp(score, 0, 100)
    return c


# ---------------------------------------------------------------- combine

def verdict(score, flags) -> str:
    sells = [f for f in flags if f["severity"] == "sell"]
    label = ("Strong candidate" if score >= 70 else "Candidate" if score >= 60 else
             "Watch" if score >= 45 else "Avoid")
    if sells and label in ("Strong candidate", "Candidate"):
        label = "Watch (red flag)"
    return label


def risk_bucket(vol, market_cap) -> str:
    if vol is None:
        return "unknown"
    if vol < 0.25 and (market_cap or 0) >= 50e9:
        return "Low"
    return "Medium" if vol <= 0.45 else "High"


def score_symbol(sym: str, conn=None, regime: Optional[str] = None) -> Dict:
    own = conn is None
    conn = conn or connect()
    sym = sym.upper()
    comp = conn.execute("SELECT Name, Sector, Industry, MarketCapitalization, ForwardPE, PEGRatio, "
                        "AnalystTargetPrice, Beta FROM company WHERE symbol=?", (sym,)).fetchone()
    name, sector, industry, mcap, fpe, peg, target, beta = comp or (sym, None, None, None, None, None, None, None)

    trend, stats = score_trend(sym)
    cards = {
        "fundamental": score_fundamental(conn, sym),
        "estimates": score_estimates(conn, sym),
        "sentiment": score_sentiment(conn, sym),
        "trend": trend,
        "smart_money": score_smart_money(conn, sym, mcap),
    }
    flags = [f for c in cards.values() for f in c.flags]
    if stats.get("drawdown") is not None:
        limit = -0.35 if risk_bucket(stats.get("volatility"), mcap) == "High" else -0.25
        if stats["drawdown"] <= limit:
            # The plan: a big drop is a sell only "with no good explanation". If the
            # business and analyst outlook are still strong, the drop is the market,
            # not the company, so it becomes a review instead of a sell.
            f_ok = (cards["fundamental"].score or 0) >= 60 and (cards["estimates"].score or 0) >= 60
            flags.append({"severity": "review" if f_ok else "sell",
                          "text": f"Safety net: {stats['drawdown'] * 100:.0f}% below 52-week high"
                                  + (" (business and estimates still strong)" if f_ok else "")})
    if stats.get("trend_break") and any(f["severity"] in ("sell", "review") for f in flags):
        flags.append({"severity": "sell", "text": "Trend break confirmed by another warning"})

    scored = {k: c.score for k, c in cards.items() if c.score is not None}
    wsum = sum(WEIGHTS[k] for k in scored)
    total = sum(WEIGHTS[k] * v for k, v in scored.items()) / wsum if wsum else None
    upside = (target / stats["price"] - 1) if target and stats.get("price") else None

    result = {
        "symbol": sym, "name": name, "sector": sector, "industry": industry,
        "as_of": datetime.now().isoformat(timespec="minutes"),
        "score": None if total is None else round(total, 1),
        "verdict": verdict(total, flags) if total is not None else "Not enough data",
        "risk_bucket": risk_bucket(stats.get("volatility"), mcap),
        "price": stats.get("price"), "market_cap_b": None if not mcap else round(mcap / 1e9, 1),
        "forward_pe": fpe, "peg": peg, "beta": beta,
        "analyst_target": target, "target_upside_pct": _pct(upside),
        "volatility_pct": _pct(stats.get("volatility"), 0), "return_12m_pct": _pct(stats.get("ret_12m")),
        "weights": WEIGHTS, "components": {k: c.as_dict() for k, c in cards.items()}, "flags": flags,
    }
    # Market pulse: can override the score (dip buys, company-specific drops).
    from .pulse import decide, dip_analysis, market_regime
    if regime is None:
        regime = market_regime(conn)["regime"]
    has_sell = any(f["severity"] == "sell" for f in flags)
    try:
        dip = dip_analysis(sym, conn, cards["fundamental"].score, cards["estimates"].score, has_sell, regime)
    except Exception as e:
        dip = {"status": f"error: {e}"}
    result["pulse"] = {"regime": regime, "dip": dip}
    result["decision"] = decide(result["verdict"], regime, dip, has_sell)
    if own:
        conn.close()
    return result


# ---------------------------------------------------------------- output

def _bar(score, width=20):
    if score is None:
        return "·" * width + "  n/a"
    filled = int(round(score / 100 * width))
    return "█" * filled + "░" * (width - filled) + f" {score:5.1f}"


def print_card(r: Dict) -> None:
    print("\n" + "═" * 78)
    print(f" {r['symbol']} · {r['name']}  ({(r['sector'] or '').title()} / {(r['industry'] or '').title()})")
    price = f"${r['price']:,.2f}" if r["price"] else "n/a"
    print(f" Price {price} · Mkt cap ${r['market_cap_b']}B · Fwd P/E {r['forward_pe']} · PEG {r['peg']} · "
          f"Target {r['target_upside_pct']:+.0f}%" if r["target_upside_pct"] is not None else f" Price {price}")
    print("─" * 78)
    print(f" DECISION ▶ {r.get('decision', '')}   (market: {r.get('pulse', {}).get('regime', '?')})")
    print(f" LONG-HOLD SCORE  {_bar(r['score'], 30)}   → {r['verdict']} · risk: {r['risk_bucket']}")
    print("─" * 78)
    for k, c in r["components"].items():
        print(f" {k.replace('_', ' ').title():<13}{int(r['weights'][k] * 100):>3}%  {_bar(c['score'])}")
        for f in c["facts"]:
            print(f"      · {f}")
    print("─" * 78)
    if r["flags"]:
        for f in r["flags"]:
            icon = {"sell": "✖ SELL RULE", "review": "! REVIEW", "watch": "~ WATCH"}[f["severity"]]
            print(f" {icon:<12} {f['text']}")
    else:
        print(" No red flags.")
    dip = r.get("pulse", {}).get("dip")
    if dip:
        from .pulse import print_dip
        print_dip(r["symbol"], dip)


def print_table(results: List[Dict]) -> None:
    print("\n" + "═" * 78)
    print(f" {'Symbol':<7}{'Score':>6}  {'Verdict':<18}{'Risk':<8}{'Fund':>5}{'Est':>5}{'Sent':>5}{'Trend':>6}{'Smart':>6}  Decision")
    for r in sorted(results, key=lambda x: -(x["score"] or 0)):
        cs = r["components"]
        f = lambda k: f"{cs[k]['score']:.0f}" if cs[k]["score"] is not None else "-"
        print(f" {r['symbol']:<7}{(r['score'] or 0):>6.1f}  {r['verdict']:<18}{r['risk_bucket']:<8}"
              f"{f('fundamental'):>5}{f('estimates'):>5}{f('sentiment'):>5}{f('trend'):>6}{f('smart_money'):>6}"
              f"  {r.get('decision', '')}")


def save(results: List[Dict]) -> str:
    out = REPORT_DIR / date.today().isoformat()
    out.mkdir(parents=True, exist_ok=True)
    for r in results:
        with open(out / f"{r['symbol']}.json", "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, default=str)
    rows = [{k: r.get(k) for k in ("symbol", "name", "sector", "decision", "score", "verdict", "risk_bucket", "price",
                               "market_cap_b", "forward_pe", "peg", "target_upside_pct", "volatility_pct",
                               "return_12m_pct")} |
            {f"{k}_score": c["score"] for k, c in r["components"].items()} |
            {"flags": " | ".join(f["text"] for f in r["flags"])} for r in results]
    pd.DataFrame(rows).sort_values("score", ascending=False).to_csv(out / "summary.csv", index=False)
    return str(out)
