"""Paths and settings for the research pipeline.

Everything the pipeline downloads or builds lives under DATA_DIR (default:
<repo>/data_store), which is git-ignored. Override with TRADENEW_DATA_DIR.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = Path(os.getenv("TRADENEW_DATA_DIR", ROOT / "data_store"))
RAW_DIR = DATA_DIR / "raw"            # untouched API responses, one file per call
WAREHOUSE_DIR = DATA_DIR / "warehouse"  # cleaned tables built from raw (later step)
LOG_DIR = DATA_DIR / "logs"
CATALOG_DB = DATA_DIR / "catalog.sqlite"  # what was fetched, when, and how it went

BASE_URL = "https://www.alphavantage.co/query"

# Plan allows 75/min; stay a little under so bursts never trip the limit.
CALLS_PER_MINUTE = int(os.getenv("AV_CALLS_PER_MINUTE", "70"))
DEFAULT_WORKERS = int(os.getenv("AV_WORKERS", "4"))


def api_key() -> str:
    key = os.getenv("ALPHA_VANTAGE_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "ALPHA_VANTAGE_API_KEY is not set. Add it to the .env file in the repo root:\n"
            "  ALPHA_VANTAGE_API_KEY=your_premium_key"
        )
    return key


def ensure_dirs() -> None:
    for d in (RAW_DIR, WAREHOUSE_DIR, LOG_DIR):
        d.mkdir(parents=True, exist_ok=True)
