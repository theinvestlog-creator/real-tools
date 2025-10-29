from __future__ import annotations
import pandas as pd
from pathlib import Path

STORE_DIR = Path("data/store/tickers")
STORE_DIR.mkdir(parents=True, exist_ok=True)

def read_csv(symbol: str) -> pd.DataFrame:
    p = STORE_DIR / f"{symbol}.csv"
    if not p.exists():
        return pd.DataFrame(columns=["date","close"])
    df = pd.read_csv(p, parse_dates=["date"])
    return df

def write_csv(symbol: str, df: pd.DataFrame) -> None:
    p = STORE_DIR / f"{symbol}.csv"
    df = df.sort_values("date").drop_duplicates(subset=["date"], keep="last")
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)

def upsert_prices(symbol: str, dates, closes) -> None:
    import pandas as pd
    existing = read_csv(symbol)
    new = pd.DataFrame({"date": pd.to_datetime(dates, unit="s"), "close": closes}).dropna()
    merged = pd.concat([existing, new], ignore_index=True)
    write_csv(symbol, merged)
