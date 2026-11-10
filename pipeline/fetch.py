"""Fetch orchestration: expand (symbols x endpoints x variants) into tasks,
skip what is already fresh, run the rest in parallel under the rate limit."""
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Optional

from . import config
from .client import AVClient, AVError
from .endpoints import Endpoint
from .store import Catalog, raw_path, write_payload

log = logging.getLogger("pipeline")


@dataclass
class Task:
    ep: Endpoint
    symbol: Optional[str]     # None for market-wide endpoints
    variant: str
    params: dict
    ttl: Optional[float]

    @property
    def label(self) -> str:
        who = self.symbol or "market"
        return f"{who:<6} {self.ep.name}" + (f" [{self.variant}]" if self.variant else "")


def build_tasks(endpoints: List[Endpoint], symbols: List[Optional[str]]) -> List[Task]:
    tasks = []
    for sym in symbols:
        for ep in endpoints:
            base = dict(ep.params)
            base["function"] = ep.function
            if sym is not None:
                base[ep.symbol_param] = sym
            variants = ep.variants() if ep.variants else [("", {}, ep.ttl_days)]
            for vid, vparams, vttl in variants:
                # Variants carry their own TTL: None = keep forever (finished news
                # month, published transcript); a number = refresh after that many days.
                tasks.append(Task(ep, sym, vid, {**base, **vparams}, vttl))
    return tasks


class Fetcher:
    def __init__(self, workers: int = config.DEFAULT_WORKERS, force: bool = False):
        config.ensure_dirs()
        self.client = AVClient()
        self.catalog = Catalog()
        self.workers = max(1, workers)
        self.force = force
        self.stop = threading.Event()   # set on daily-quota errors
        self.counts = {}
        self._lock = threading.Lock()

    def _bump(self, key):
        with self._lock:
            self.counts[key] = self.counts.get(key, 0) + 1

    def _get_paginated_news(self, params: dict, max_pages: int = 12) -> dict:
        """NEWS_SENTIMENT returns at most `limit` (1,000) newest articles per call.
        When a window is full, ask again for articles older than the oldest one
        received, until the whole window is covered."""
        cap = int(params.get("limit", 50))
        start = params.get("time_from", "")
        p = dict(params)
        feed, seen, pages, payload = [], set(), 0, {}
        while pages < max_pages:
            payload = self.client.get(p)
            pages += 1
            batch = payload.get("feed", [])
            fresh = [a for a in batch if a.get("url") not in seen]
            seen.update(a.get("url") for a in fresh)
            feed.extend(fresh)
            if len(batch) < cap or not fresh:
                break
            oldest = min(a["time_published"] for a in batch)[:13]  # YYYYMMDDTHHMM
            if oldest <= start:
                break
            p = {**p, "time_to": oldest}
        payload["feed"] = feed
        payload["items"] = str(len(feed))
        payload["pages_fetched"] = pages
        if pages >= max_pages:
            log.warning("news for %s hit the %d-page limit; window may be incomplete",
                        params.get("tickers") or params.get("topics"), max_pages)
        return payload

    def _run_one(self, t: Task) -> str:
        sym_key = t.symbol or "*"
        if self.stop.is_set():
            return "skipped"
        ext = "csv" if t.ep.datatype == "csv" else ("json.gz" if t.ep.compress else "json")
        path = raw_path(t.ep.name, t.symbol, t.variant, ext)
        try:
            if t.ep.paginate:
                payload = self._get_paginated_news(t.params)
            else:
                payload = self.client.get(t.params, t.ep.datatype)
        except AVError as e:
            if e.kind == "quota":
                self.stop.set()
            self.catalog.record(t.ep.name, sym_key, t.variant, e.kind, message=e.message)
            log.warning("%s -> %s: %s", t.label, e.kind, e.message[:160])
            return e.kind
        status = "empty" if (t.ep.is_empty and t.ep.is_empty(payload)) else "ok"
        nbytes = write_payload(path, payload)
        self.catalog.record(t.ep.name, sym_key, t.variant, status, path=path, nbytes=nbytes)
        log.info("%s -> %s (%s KB)", t.label, status, round(nbytes / 1024, 1))
        return status

    def run(self, tasks: List[Task]) -> dict:
        todo = [t for t in tasks
                if self.force or not self.catalog.is_fresh(t.ep.name, t.symbol or "*", t.variant, t.ttl)]
        skipped = len(tasks) - len(todo)
        if skipped:
            self.counts["cached"] = skipped
        mins = len(todo) / config.CALLS_PER_MINUTE
        log.info("%d tasks: %d already fresh, %d to fetch (~%.1f min at %d/min)",
                 len(tasks), skipped, len(todo), mins, config.CALLS_PER_MINUTE)
        if not todo:
            return self.counts

        done = 0
        with ThreadPoolExecutor(max_workers=self.workers) as pool:
            futures = {pool.submit(self._run_one, t): t for t in todo}
            for fut in as_completed(futures):
                try:
                    status = fut.result()
                except Exception as e:  # unexpected bug: log and keep going
                    t = futures[fut]
                    log.exception("%s crashed: %s", t.label, e)
                    status = "crash"
                self._bump(status)
                done += 1
                if done % 25 == 0 or done == len(todo):
                    log.info("progress %d/%d  (API calls so far: %d)", done, len(todo), self.client.calls_made)
        if self.stop.is_set():
            log.error("Stopped early: Alpha Vantage reported a daily quota limit. "
                      "Check that the .env key is the premium one.")
        return self.counts
