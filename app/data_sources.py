# ------------------------------------------------------------
#  Market Data Sources (External Inputs)
#
#  Purpose:
#  --------
#  This file is responsible for pulling raw market data
#  from external sources (web APIs, CSV feeds).
#
#  Responsibilities:
#  -----------------
#  • Fetch data over HTTPS
#  • Parse raw responses (CSV)
#  • Handle failures gracefully
#  • NEVER apply trading logic or thresholds
#
#  Design Philosophy:
#  ------------------
#  • One function = one data source
#  • Fail safely (return None, not bad numbers)
#  • Never crash the app because of bad data
# ------------------------------------------------------------


# -----------------------
#  Imports
# -----------------------
# csv / io:
#   Used to parse CSV text returned by data providers
import csv
import io
import re
import json

# dataclass:
#   Provides a clean, explicit structure for return values
from dataclasses import dataclass

# Optional, Tuple:
#   Used to clearly express "this value may be missing"
#   and to annotate parsed CSV rows
from typing import Optional, Tuple

# requests:
#   Handles HTTPS requests to external data providers
import requests


# -----------------------
#  PullResult Data Model
# -----------------------
# This is the standard return type for ALL data pulls.
#
# value:
#   • The numeric value we care about (float)
#   • None if data is unavailable or invalid
#
# error:
#   • Human-readable error message (for debugging)
#   • None if everything worked
#
# Why this exists:
#   • Separates "data missing" from "program crashed"
#   • Allows UI to degrade gracefully
@dataclass
class PullResult:
    value: Optional[float]
    error: Optional[str] = None


# -----------------------
#  Low-Level HTTP Helper
# -----------------------
# Purpose:
#   Centralized helper for HTTP GET requests.
#
# Why:
#   • Keeps timeout handling consistent
#   • Raises HTTP errors immediately
#   • Makes fetch functions simpler and safer
def _get_text(url: str, timeout: int = 10) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()   # Raises exception for 4xx / 5xx
    return r.text

# -----------------------
#  Barchart Quote Scrape Helper
# -----------------------
# Purpose:
#   Barchart pages embed quote data in the HTML.
#   We scrape the "lastPrice" field for simple indicators like $HIGN / $LOWN.
#
# Note:
#   This is intentionally "good enough" for a monitor.
def _barchart_last_price(symbol: str) -> PullResult:
    try:
        url = f"https://www.barchart.com/stocks/quotes/{symbol}"
        html = _get_text(url)

        # Common embedded pattern in page HTML (may change over time)
        m = re.search(r'"lastPrice"\s*:\s*([0-9]+(?:\.[0-9]+)?)', html)
        if not m:
            return PullResult(None, f"Barchart scrape failed: lastPrice not found for {symbol}")

        return PullResult(float(m.group(1)), None)

    except Exception as e:
        return PullResult(None, f"Barchart scrape failed for {symbol}: {e}")


# -----------------------
#  VIX Data Source (FRED)
# -----------------------
# Source:
#   Federal Reserve Economic Data (FRED)
#   Series: VIXCLS
#
# Format:
#   CSV with columns:
#     DATE, VIXCLS
#
# Behavior:
#   • Iterates through all rows
#   • Keeps the most recent valid value
#   • Ignores missing values (".")
#
# Output:
#   PullResult(value=<float>, error=None)
#   PullResult(value=None, error="...") on failure
def fetch_vix_close_fred() -> PullResult:
    try:
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
        text = _get_text(url)

        reader = csv.DictReader(io.StringIO(text))
        latest = None

        for row in reader:
            val = row.get("VIXCLS", "").strip()
            if val and val != ".":
                latest = float(val)

        return PullResult(latest, None)

    except Exception as e:
        # Never let exceptions escape this layer
        return PullResult(None, f"VIX pull failed: {e}")


# -----------------------
#  CSV Parsing Helper (Stooq)
# -----------------------
# Purpose:
#   Normalize Stooq daily price CSV data.
#
# Expected Format:
#   Date,Open,High,Low,Close,Volume
#
# Output:
#   List of tuples:
#     [(date_string, close_price), ...]
#
# Note:
#   Ordering is not guaranteed by source,
#   so sorting is handled later.
def _parse_stooq_daily_csv(text: str) -> list[Tuple[str, float]]:
    reader = csv.DictReader(io.StringIO(text))
    rows = []

    for row in reader:
        date = row.get("Date") or row.get("date")
        close = row.get("Close") or row.get("close")

        if not date or not close:
            continue

        rows.append((date, float(close)))

    return rows


# -----------------------
#  IWV Percent Change (Stooq)
# -----------------------
# Source:
#   Stooq (free daily ETF price data)
#
# Goal:
#   Compute DAILY percent change:
#
#     (latest_close / previous_close - 1) * 100
#
# Safety Checks:
#   • Ensure at least 2 data points exist
#   • Prevent division by zero
#   • Catch all exceptions
#
# Output:
#   PullResult(value=<float>, error=None)
#   PullResult(value=None, error="...") on failure
def fetch_iwv_pct_change_stooq() -> PullResult:
    try:
        url = "https://stooq.com/q/d/l/?s=iwv.us&i=d"
        text = _get_text(url)

        rows = _parse_stooq_daily_csv(text)

        # Normalize ordering (oldest → newest)
        rows_sorted = sorted(rows, key=lambda x: x[0])

        if len(rows_sorted) < 2:
            return PullResult(None, "Not enough IWV data points.")

        _, prev_close = rows_sorted[-2]
        _, last_close = rows_sorted[-1]

        if prev_close == 0:
            return PullResult(None, "Previous close was 0 (invalid).")

        pct = (last_close / prev_close - 1.0) * 100.0
        return PullResult(round(pct, 2), None)

    except Exception as e:
        # Data problems should never crash the app
        return PullResult(None, f"IWV pull failed: {e}")


# -----------------------
#  HH / LL (NYSE 52-Week Highs - Lows) (TradingView Scanner)
# -----------------------
# Source:
#   TradingView scanner endpoint (JSON)
#
# What it measures:
#   Count of NYSE-listed stocks hitting 52-week highs vs 52-week lows.
#
# Output:
#   HH/LL = highs_count - lows_count
#
# Notes:
#   • This is an approximation of "new highs/new lows"
#   • It is consistent and automatable (good for a monitor)
def fetch_nyse_hh_ll_tv() -> PullResult:
    try:
        url = "https://scanner.tradingview.com/america/scan"

        payload = {
            "filter": [
                {"left": "exchange", "operation": "equal", "right": "NYSE"},
            ],
            "symbols": {"query": {"types": []}, "tickers": []},
            "columns": ["name"],
            "sort": {"sortBy": "name", "sortOrder": "asc"},
            "range": [0, 1]
        }

        # We'll do two scans:
        #  - one for 52-week highs
        #  - one for 52-week lows
        #
        # TradingView fields:
        #   "price_52_week_high" / "price_52_week_low" exist,
        #   and we compare last close to those levels.

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }

        def count_matching(extra_filter):
            p = dict(payload)
            p["filter"] = payload["filter"] + extra_filter
            r = requests.post(url, headers=headers, data=json.dumps(p), timeout=10)
            r.raise_for_status()
            data = r.json()
            return int(data.get("totalCount", 0))

        highs = count_matching([
            {"left": "close", "operation": "equal", "right": "price_52_week_high"}
        ])

        lows = count_matching([
            {"left": "close", "operation": "equal", "right": "price_52_week_low"}
        ])

        hh_ll = highs - lows
        return PullResult(float(hh_ll), None)

    except Exception as e:
        return PullResult(None, f"HH/LL pull failed (TradingView): {e}")


