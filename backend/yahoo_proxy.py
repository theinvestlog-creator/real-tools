from __future__ import annotations
import time, requests
from typing import Dict, Any, Optional

BASE_URL = "https://trudov.com/yahoo.php"
TOKEN = "mySuperStrongSecret123"

# simple per-ticker throttle
_last_call: Dict[str, float] = {}

def fetch_chart(symbol: str, interval: str = "1d", range_: str = "max", min_interval=1.0, max_retries=4) -> Dict[str, Any]:
    now = time.time()
    last = _last_call.get(symbol, 0.0)
    wait = max(0.0, min_interval - (now - last))
    if wait > 0:
        time.sleep(wait)

    params = {"token": TOKEN, "symbol": symbol, "interval": interval, "range": range_}
    backoff = 1.0
    for attempt in range(max_retries):
        resp = requests.get(BASE_URL, params=params, timeout=20)
        if resp.status_code == 200:
            _last_call[symbol] = time.time()
            return resp.json()
        if resp.status_code in (429, 503):
            time.sleep(backoff)
            backoff *= 2
            continue
        resp.raise_for_status()
    raise RuntimeError(f"Yahoo proxy failed for {symbol} after {max_retries} attempts")
