"""Command line for the research pipeline.

  python -m pipeline check                         # is the key premium and working?
  python -m pipeline market                        # market-wide data (universe, macro, calendar, crypto)
  python -m pipeline fetch AAPL MSFT NVDA          # everything for these stocks
  python -m pipeline fetch SPY QQQ --etf           # benchmark / index funds
  python -m pipeline fetch AAPL --groups prices,forward
  python -m pipeline pulse --fetch NVDA            # market mood + why NVDA dropped
  python -m pipeline score MSFT NVDA IBM           # scorecards with the pulse decision
  python -m pipeline status [SYMBOL]               # what is stored locally
"""
import argparse
import logging
import sys
from datetime import datetime

from . import config, endpoints
from .client import AVClient, AVError
from .fetch import Fetcher, build_tasks
from .store import Catalog


def _setup_logging(verbose: bool) -> None:
    config.ensure_dirs()
    logfile = config.LOG_DIR / f"run_{datetime.now():%Y%m%d}.log"
    fmt = "%(asctime)s %(levelname)-7s %(message)s"
    console = logging.StreamHandler(sys.stdout)
    if not verbose:  # console shows warnings + progress; the log file keeps every call
        console.addFilter(lambda r: r.levelno >= logging.WARNING
                          or "progress" in r.getMessage() or "tasks:" in r.getMessage())
    handlers = [logging.FileHandler(logfile, encoding="utf-8"), console]
    logging.basicConfig(level=logging.INFO, format=fmt, datefmt="%H:%M:%S", handlers=handlers)


def _groups(arg, default, allowed):
    if not arg:
        return default
    groups = [g.strip() for g in arg.split(",") if g.strip()]
    if groups == ["all"]:
        return allowed
    bad = [g for g in groups if g not in allowed]
    if bad:
        raise SystemExit(f"Unknown group(s): {bad}. Choose from: {', '.join(allowed)}")
    return groups


def _summary(counts: dict) -> None:
    order = ["ok", "empty", "cached", "premium", "invalid", "info", "quota", "http", "skipped", "crash"]
    parts = [f"{k}={counts[k]}" for k in order if counts.get(k)]
    print("\nResult:", ", ".join(parts) or "nothing to do")
    if counts.get("premium"):
        print("  'premium' = the key was refused for a premium endpoint (is .env using the new key?)")
    if counts.get("empty"):
        print("  'empty' = valid call with no data yet (e.g. future transcript quarter). Retried in 7 days.")
    print(f"Data folder: {config.DATA_DIR}")


def cmd_check(_args) -> None:
    client = AVClient()
    tests = [
        ("OVERVIEW (premium)", {"function": "OVERVIEW", "symbol": "IBM"}),
        ("NEWS_SENTIMENT (premium)", {"function": "NEWS_SENTIMENT", "tickers": "IBM", "limit": "5"}),
    ]
    ok = True
    for label, params in tests:
        try:
            data = client.get(params)
            hint = data.get("Name") or f"{len(data.get('feed', []))} articles"
            print(f"  OK    {label}: {hint}")
        except AVError as e:
            ok = False
            print(f"  FAIL  {label}: {e.kind} - {e.message[:200]}")
    print("\nKey works with premium endpoints." if ok else "\nFix the key before fetching.")


def cmd_market(args) -> None:
    # pulse_news is ~900 calls the first time, so it runs only via `pulse --fetch`
    # or when asked for explicitly (--groups pulse_news / all).
    default = [g for g in endpoints.ALL_GLOBAL_GROUPS if g != "pulse_news"]
    groups = _groups(args.groups, default, endpoints.ALL_GLOBAL_GROUPS)
    tasks = build_tasks(endpoints.global_endpoints(groups), [None])
    _summary(Fetcher(args.workers, args.force).run(tasks))


def cmd_fetch(args) -> None:
    symbols = sorted({s.strip().upper() for s in args.symbols if s.strip()})
    default = endpoints.DEFAULT_ETF_GROUPS if args.etf else endpoints.DEFAULT_STOCK_GROUPS
    groups = _groups(args.groups, default, endpoints.ALL_SYMBOL_GROUPS)
    if args.news_months is not None:
        endpoints.NEWS_MONTHS = args.news_months
    tasks = build_tasks(endpoints.symbol_endpoints(groups), symbols)
    print(f"Fetching {len(symbols)} symbol(s), groups: {', '.join(groups)}")
    _summary(Fetcher(args.workers, args.force).run(tasks))


def cmd_build(args) -> None:
    from .build import build
    summary = build(args.symbols or None)
    print(f"Market tables: {summary.pop('market_rows')} rows")
    for sym, counts in summary.items():
        print(f"  {sym:<6} " + "  ".join(f"{k}={v}" for k, v in counts.items()))
    print(f"Warehouse: {config.WAREHOUSE_DIR}")


def cmd_score(args) -> None:
    from .build import build
    from .score import print_card, print_table, save, score_symbol
    from .build import connect
    from .endpoints import PULSE_ETFS
    from .pulse import print_market
    symbols = [s.upper() for s in args.symbols]
    build(symbols + list(PULSE_ETFS))            # these stocks + market/sector ETFs (prices only)
    conn = connect()
    regime = print_market(conn)["regime"]
    results = [score_symbol(s, conn, regime) for s in symbols]
    conn.close()
    if not args.table_only:
        for r in results:
            print_card(r)
    print_table(results)
    print(f"\nSaved: {save(results)}")


def cmd_pulse(args) -> None:
    """Market mood + news themes + dip check for any symbols given."""
    from .build import build, connect
    from .endpoints import PULSE_ETFS
    from .pulse import dip_analysis, print_dip, print_market
    if args.fetch:
        etfs = list(PULSE_ETFS)
        print(f"Fetching prices for {len(etfs)} market/sector ETFs, then {endpoints.PULSE_NEWS_DAYS} days "
              f"of market news ({len(endpoints.PULSE_TOPICS)} topics)")
        tasks = build_tasks(endpoints.symbol_endpoints(["prices"]), etfs)
        tasks += build_tasks(endpoints.global_endpoints(["pulse_news"]), [None])
        _summary(Fetcher(args.workers, args.force).run(tasks))
    symbols = [s.upper() for s in args.symbols]
    build(symbols + list(PULSE_ETFS))
    conn = connect()
    regime = print_market(conn)["regime"]
    for s in symbols:
        print_dip(s, dip_analysis(s, conn, regime=regime))
    if symbols:
        print("\n(Dip verdicts here ignore fundamentals; `score` combines both.)")
    conn.close()


def cmd_run(args) -> None:
    """fetch -> build -> score in one go."""
    cmd_fetch(args)
    args.table_only = False
    cmd_score(args)


def cmd_status(args) -> None:
    cat = Catalog()
    if args.symbol:
        sym = args.symbol.upper()
        rows = cat.query(
            "SELECT endpoint, variant, status, bytes, fetched_at, message FROM fetch_log "
            "WHERE symbol=? ORDER BY endpoint, variant DESC", (sym,))
        if not rows:
            print(f"Nothing stored for {sym} yet.")
            return
        print(f"{sym}: {len(rows)} stored items\n")
        for ep, var, status, nbytes, ts, msg in rows:
            size = f"{(nbytes or 0) / 1024:8.1f} KB" if nbytes else " " * 11
            note = f"  {msg[:70]}" if status not in ("ok", "empty") else ""
            print(f"  {ep:<24}{var:<10}{status:<8}{size}  {ts[:16]}{note}")
        return
    rows = cat.query(
        "SELECT symbol, COUNT(*), SUM(status='ok'), SUM(status='empty'), "
        "SUM(status NOT IN ('ok','empty')), ROUND(SUM(COALESCE(bytes,0))/1048576.0, 1), MAX(fetched_at) "
        "FROM fetch_log GROUP BY symbol ORDER BY symbol")
    if not rows:
        print("Nothing stored yet. Run: python -m pipeline check")
        return
    print(f"{'symbol':<8}{'items':>6}{'ok':>6}{'empty':>7}{'failed':>8}{'MB':>8}  last fetch (UTC)")
    for sym, n, ok, empty, failed, mb, last in rows:
        print(f"{('market' if sym == '*' else sym):<8}{n:>6}{ok:>6}{empty:>7}{failed:>8}{mb:>8}  {last[:16]}")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="python -m pipeline", description="TradeNew research pipeline")
    p.add_argument("-v", "--verbose", action="store_true", help="print every call")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="test the API key against premium endpoints (2 calls)")

    m = sub.add_parser("market", help="fetch market-wide data")
    m.add_argument("--groups", help=f"comma list: {','.join(endpoints.ALL_GLOBAL_GROUPS)}")

    f = sub.add_parser("fetch", help="fetch data for symbols")
    f.add_argument("symbols", nargs="+")
    f.add_argument("--groups", help=f"comma list or 'all': {','.join(endpoints.ALL_SYMBOL_GROUPS)}")
    f.add_argument("--etf", action="store_true", help="symbols are ETFs (prices + fund profile)")
    f.add_argument("--news-months", type=int, help=f"months of news history (default {endpoints.NEWS_MONTHS})")

    r = sub.add_parser("run", help="fetch + build + score in one go")
    r.add_argument("symbols", nargs="+")
    r.add_argument("--groups", help="comma list or 'all'")
    r.add_argument("--news-months", type=int)
    r.set_defaults(etf=False)

    for sp in (m, f, r):
        sp.add_argument("--force", action="store_true", help="refetch even if fresh")
        sp.add_argument("--workers", type=int, default=config.DEFAULT_WORKERS)

    b = sub.add_parser("build", help="turn raw files into warehouse tables (no API calls)")
    b.add_argument("symbols", nargs="*", help="default: every stored symbol")

    pu = sub.add_parser("pulse", help="market mood, news themes, and why a stock dropped")
    pu.add_argument("symbols", nargs="*")
    pu.add_argument("--fetch", action="store_true", help="first fetch ETF prices + market news (API calls)")
    pu.add_argument("--force", action="store_true")
    pu.add_argument("--workers", type=int, default=config.DEFAULT_WORKERS)

    sc = sub.add_parser("score", help="long-hold scorecard from local data (no API calls)")
    sc.add_argument("symbols", nargs="+")
    sc.add_argument("--table-only", action="store_true", help="only the comparison table")

    s = sub.add_parser("status", help="show what is stored")
    s.add_argument("symbol", nargs="?")

    args = p.parse_args(argv)
    _setup_logging(args.verbose)
    {"check": cmd_check, "market": cmd_market, "fetch": cmd_fetch, "status": cmd_status,
     "build": cmd_build, "score": cmd_score, "run": cmd_run, "pulse": cmd_pulse}[args.cmd](args)


if __name__ == "__main__":
    main()
