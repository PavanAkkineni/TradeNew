"""Registry of every Alpha Vantage endpoint the pipeline uses.

Each Endpoint knows its API function, which group it belongs to, how long a
saved copy stays fresh (ttl_days; None = never refetch), and how to expand
into one or more calls ("variants") for a symbol.

Adding an endpoint = adding one entry here. Nothing else needs to change.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Callable, List, Optional, Tuple

Variant = Tuple[str, dict, Optional[float]]  # (variant_id, extra params, ttl override)


@dataclass
class Endpoint:
    name: str                 # folder name under data_store/raw/
    function: str             # Alpha Vantage `function=`
    group: str
    scope: str = "symbol"     # "symbol" (needs a ticker) or "global"
    ttl_days: Optional[float] = 7
    datatype: str = "json"
    params: dict = field(default_factory=dict)
    symbol_param: str = "symbol"
    variants: Optional[Callable[[], List[Variant]]] = None
    is_empty: Optional[Callable[[object], bool]] = None
    compress: bool = False    # store as .json.gz (news is large and compresses ~10x)
    paginate: bool = False    # news: keep paging back in time while a call hits the 1,000 cap


# ---------- variant builders ----------

def _months_back(n: int) -> List[Variant]:
    """Calendar months, newest first. Finished months never change, so they
    are kept forever; the current month refreshes daily."""
    today = date.today()
    y, m = today.year, today.month
    out = []
    for i in range(n):
        start = date(y, m, 1)
        ny, nm = (y + 1, 1) if m == 12 else (y, m + 1)
        end = date(ny, nm, 1)
        params = {"time_from": start.strftime("%Y%m%dT0000"), "sort": "LATEST", "limit": "1000"}
        if i > 0:
            params["time_to"] = end.strftime("%Y%m%dT0000")
        out.append((start.strftime("%Y-%m"), params, 1 if i == 0 else None))
        y, m = (y - 1, 12) if m == 1 else (y, m - 1)
    return out


def _fiscal_quarters(n: int) -> List[Variant]:
    """Transcripts are labelled by the company's *fiscal* quarter, which can run
    ahead of the calendar (e.g. Microsoft). Start one year ahead and walk back;
    labels with no transcript yet come back empty and are retried in 7 days."""
    today = date.today()
    y, q = today.year + 1, (today.month - 1) // 3 + 1
    out = []
    for _ in range(n):
        out.append((f"{y}Q{q}", {"quarter": f"{y}Q{q}"}, None))
        y, q = (y - 1, 4) if q == 1 else (y, q - 1)
    return out


NEWS_MONTHS = 12
TRANSCRIPT_QUARTERS = 9   # ~1 future-year window + the last ~5 real quarters


def _empty_transcript(d) -> bool:
    return isinstance(d, dict) and not d.get("transcript")


def _empty_news(d) -> bool:
    return isinstance(d, dict) and not d.get("feed")


def _empty_list_payload(d) -> bool:
    if isinstance(d, dict):
        data = d.get("data")
        if data is not None:
            return len(data) == 0
    return False


# ---------- per-symbol endpoints ----------

SYMBOL_ENDPOINTS = [
    # screen: one call that summarises a company (ratios, growth, targets)
    Endpoint("overview", "OVERVIEW", "screen", ttl_days=7),

    # prices: full daily history (25+ yrs) is the backtest archive
    Endpoint("daily_adjusted", "TIME_SERIES_DAILY_ADJUSTED", "prices", ttl_days=1,
             params={"outputsize": "full"}),
    Endpoint("weekly_adjusted", "TIME_SERIES_WEEKLY_ADJUSTED", "prices", ttl_days=1),

    # financials: statements, earnings history, share count, payouts
    Endpoint("income_statement", "INCOME_STATEMENT", "financials", ttl_days=30),
    Endpoint("balance_sheet", "BALANCE_SHEET", "financials", ttl_days=30),
    Endpoint("cash_flow", "CASH_FLOW", "financials", ttl_days=30),
    Endpoint("earnings", "EARNINGS", "financials", ttl_days=7),
    Endpoint("shares_outstanding", "SHARES_OUTSTANDING", "financials", ttl_days=30),
    Endpoint("dividends", "DIVIDENDS", "financials", ttl_days=30, is_empty=_empty_list_payload),
    Endpoint("splits", "SPLITS", "financials", ttl_days=90, is_empty=_empty_list_payload),

    # forward-looking: analyst EPS / revenue estimates and their revisions
    Endpoint("earnings_estimates", "EARNINGS_ESTIMATES", "forward", ttl_days=7),

    # smart money: insiders and institutions
    Endpoint("insider_transactions", "INSIDER_TRANSACTIONS", "smart_money", ttl_days=7,
             is_empty=_empty_list_payload),
    Endpoint("institutional_holdings", "INSTITUTIONAL_HOLDINGS", "smart_money", ttl_days=30),

    # sentiment: monthly news windows + earnings-call transcripts
    Endpoint("news_sentiment", "NEWS_SENTIMENT", "sentiment", ttl_days=1,
             symbol_param="tickers", variants=lambda: _months_back(NEWS_MONTHS),
             is_empty=_empty_news, compress=True, paginate=True),
    Endpoint("earnings_transcript", "EARNINGS_CALL_TRANSCRIPT", "transcripts", ttl_days=None,
             variants=lambda: _fiscal_quarters(TRANSCRIPT_QUARTERS),
             is_empty=_empty_transcript),

    # ETFs only (fund profile + holdings)
    Endpoint("etf_profile", "ETF_PROFILE", "etf", ttl_days=30),

    # options mood (previous session); optional
    Endpoint("put_call_ratio", "HISTORICAL_PUT_CALL_RATIO", "options", ttl_days=1),
]

# Groups fetched for a stock when --groups is not given.
DEFAULT_STOCK_GROUPS = ["screen", "prices", "financials", "forward", "smart_money",
                        "sentiment", "transcripts"]
# Sensible default for ETFs / benchmarks (SPY, QQQ, VOO...).
DEFAULT_ETF_GROUPS = ["prices", "etf"]


# ---------- market-wide endpoints ----------

def _g(name, function, group, ttl, datatype="json", **params):
    return Endpoint(name, function, group, scope="global", ttl_days=ttl,
                    datatype=datatype, params=params)


GLOBAL_ENDPOINTS = [
    _g("listing_active", "LISTING_STATUS", "universe", 7, "csv"),
    _g("listing_delisted", "LISTING_STATUS", "universe", 30, "csv", state="delisted"),
    _g("earnings_calendar", "EARNINGS_CALENDAR", "calendar", 1, "csv", horizon="12month"),

    _g("treasury_10y", "TREASURY_YIELD", "macro", 7, interval="monthly", maturity="10year"),
    _g("treasury_2y", "TREASURY_YIELD", "macro", 7, interval="monthly", maturity="2year"),
    _g("fed_funds_rate", "FEDERAL_FUNDS_RATE", "macro", 7, interval="monthly"),
    _g("cpi", "CPI", "macro", 7, interval="monthly"),
    _g("inflation", "INFLATION", "macro", 30),
    _g("unemployment", "UNEMPLOYMENT", "macro", 7),
    _g("nonfarm_payroll", "NONFARM_PAYROLL", "macro", 7),
    _g("retail_sales", "RETAIL_SALES", "macro", 7),
    _g("real_gdp", "REAL_GDP", "macro", 30, interval="quarterly"),

    _g("crypto_btc_weekly", "DIGITAL_CURRENCY_WEEKLY", "crypto", 1, symbol="BTC", market="USD"),
    _g("crypto_eth_weekly", "DIGITAL_CURRENCY_WEEKLY", "crypto", 1, symbol="ETH", market="USD"),
]

def _days_back(n: int) -> List[Variant]:
    """One window per calendar day, newest first. Market-wide topics publish far
    more than 1,000 articles a month, so a daily window (up to 1,000 articles
    each) gives an even sample across every day, which a daily mood series needs."""
    today = date.today()
    out = []
    for i in range(n):
        d = date.fromordinal(today.toordinal() - i)
        nxt = date.fromordinal(d.toordinal() + 1)
        params = {"time_from": d.strftime("%Y%m%dT0000"), "time_to": nxt.strftime("%Y%m%dT0000"),
                  "sort": "LATEST", "limit": "1000"}
        out.append((d.isoformat(), params, 0.25 if i == 0 else (1 if i == 1 else None)))
    return out


# Market-wide news by topic (no ticker filter): the "market pulse" news feed.
PULSE_NEWS_DAYS = 180
PULSE_TOPICS = ["financial_markets", "economy_macro", "economy_monetary", "economy_fiscal", "technology"]
for _topic in PULSE_TOPICS:
    GLOBAL_ENDPOINTS.append(Endpoint(
        f"market_news_{_topic}", "NEWS_SENTIMENT", "pulse_news", scope="global", ttl_days=1,
        params={"topics": _topic}, variants=lambda: _days_back(PULSE_NEWS_DAYS),
        is_empty=_empty_news, compress=True))

# ETFs the pulse layer watches: market, fear gauge, sectors and themes.
# Each stock is matched to the sector ETF it actually moves with (by correlation).
PULSE_ETFS = {
    "SPY": "S&P 500", "QQQ": "Nasdaq-100", "IWM": "Small caps (Russell 2000)",
    "VIXY": "Fear gauge (VIX futures)",
    "XLK": "Technology", "SMH": "Semiconductors / AI chips", "IGV": "Software",
    "XLF": "Financials", "XLE": "Energy", "XLV": "Health care", "XLY": "Consumer discretionary",
    "XLP": "Consumer staples", "XLI": "Industrials", "XLU": "Utilities", "XLRE": "Real estate",
    "XLB": "Materials", "XLC": "Communication services",
}

ALL_GLOBAL_GROUPS = sorted({e.group for e in GLOBAL_ENDPOINTS})
ALL_SYMBOL_GROUPS = sorted({e.group for e in SYMBOL_ENDPOINTS})


def symbol_endpoints(groups: List[str]) -> List[Endpoint]:
    return [e for e in SYMBOL_ENDPOINTS if e.group in groups]


def global_endpoints(groups: List[str]) -> List[Endpoint]:
    return [e for e in GLOBAL_ENDPOINTS if e.group in groups]
