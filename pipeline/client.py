"""Alpha Vantage HTTP client: rate limiting, retries and error classification.

Alpha Vantage answers most problems with HTTP 200 and a JSON body such as
{"Information": "..."} or {"Error Message": "..."}, so every response is
inspected before it is treated as data.
"""
import json
import logging
import threading
import time

import requests

from . import config

log = logging.getLogger("pipeline")


class AVError(Exception):
    """kind: premium | quota | invalid | info | http"""

    def __init__(self, kind: str, message: str):
        super().__init__(f"{kind}: {message}")
        self.kind = kind
        self.message = message


class RateLimiter:
    """Thread-safe pacing: calls start evenly spaced (60/per_minute s apart).
    Even spacing avoids the bursts that Alpha Vantage throttles, and it can
    never exceed `per_minute` in any 60 s window."""

    def __init__(self, per_minute: int):
        self.interval = 60.0 / per_minute
        self.next_at = 0.0
        self.lock = threading.Lock()

    def wait(self) -> None:
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next_at)
            self.next_at = start + self.interval
        if start > now:
            time.sleep(start - now)


class AVClient:
    def __init__(self, per_minute: int = config.CALLS_PER_MINUTE):
        self.key = config.api_key()
        self.limiter = RateLimiter(per_minute)
        self.session = requests.Session()
        self.calls_made = 0
        self._count_lock = threading.Lock()

    def get(self, params: dict, datatype: str = "json"):
        """Return parsed JSON (dict/list) or CSV text. Raises AVError."""
        query = dict(params)
        if datatype == "csv":
            query["datatype"] = "csv"
        query["apikey"] = self.key

        last_error = "unknown"
        for attempt in range(6):
            self.limiter.wait()
            with self._count_lock:
                self.calls_made += 1
            try:
                r = self.session.get(config.BASE_URL, params=query, timeout=90)
            except requests.RequestException as e:
                last_error = f"network: {e.__class__.__name__}"
                time.sleep(2 ** attempt)
                continue

            if r.status_code == 429 or r.status_code >= 500:
                last_error = f"HTTP {r.status_code}"
                time.sleep(5 * (attempt + 1))
                continue
            if r.status_code != 200:
                raise AVError("http", f"HTTP {r.status_code}")

            text = r.text
            if datatype == "csv" and not text.lstrip().startswith("{"):
                if not text.strip():
                    raise AVError("info", "empty CSV response")
                return text

            try:
                data = json.loads(text)
            except ValueError:
                raise AVError("invalid", f"non-JSON response: {text[:120]!r}")

            problem = self._classify(data)
            if problem is None:
                return data
            if problem.kind == "throttle":
                last_error = problem.message
                wait = 20 * (attempt + 1)
                log.info("throttled on %s, retrying in %ss", params.get("function"), wait)
                time.sleep(wait)
                continue
            raise problem

        raise AVError("http", f"gave up after retries ({last_error})")

    @staticmethod
    def _classify(data):
        """Return None for real data, or an AVError describing the problem."""
        if not isinstance(data, dict) or len(data) > 2:
            return None
        msg = data.get("Error Message") or data.get("Note") or data.get("Information")
        if not msg:
            return None
        low = msg.lower()
        # Burst messages also mention plans/"premium", so check throttling first.
        if any(w in low for w in ("per minute", "per second", "frequency", "burst",
                                  "spreading out", "sparingly")):
            return AVError("throttle", msg)
        if "per day" in low:
            return AVError("quota", msg)
        if "premium" in low or "subscribe" in low or "entitlement" in low:
            return AVError("premium", msg)
        if "Error Message" in data or "invalid" in low:
            return AVError("invalid", msg)
        return AVError("info", msg)
