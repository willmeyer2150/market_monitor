import csv
import io
from dataclasses import dataclass
from typing import Optional, Tuple

import requests


@dataclass
class PullResult:
    value: Optional[float]
    error: Optional[str] = None


def _get_text(url: str, timeout: int = 10) -> str:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.text


def fetch_vix_close_fred() -> PullResult:
    """
    Pull latest VIX close from FRED series VIXCLS as CSV.
    Returns the most recent non-missing value.
    """
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
        return PullResult(None, f"VIX pull failed: {e}")


def _parse_stooq_daily_csv(text: str) -> list[Tuple[str, float]]:
    """
    Stooq daily CSV format is typically:
    Date,Open,High,Low,Close,Volume
    Return list of (date, close) sorted as given (usually descending).
    """
    reader = csv.DictReader(io.StringIO(text))
    rows = []
    for row in reader:
        date = row.get("Date") or row.get("date")
        close = row.get("Close") or row.get("close")
        if not date or not close:
            continue
        rows.append((date, float(close)))
    return rows


def fetch_iwv_pct_change_stooq() -> PullResult:
    """
    Pull daily closes for IWV from Stooq and compute % change vs prior close:
      (close_today / close_prev - 1) * 100
    """
    try:
        url = "https://stooq.com/q/d/l/?s=iwv.us&i=d"
        text = _get_text(url)
        rows = _parse_stooq_daily_csv(text)

        # Some sources return ascending (oldest->newest), others descending.
        # We’ll normalize by sorting by date.
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
        return PullResult(None, f"IWV pull failed: {e}")
