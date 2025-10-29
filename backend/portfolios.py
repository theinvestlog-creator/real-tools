from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .store import read_csv

OUT_DIR = Path("public/data/portfolios")

def build_portfolios(registry_path: str, out_root: str = str(OUT_DIR)) -> None:
    reg = json.loads(Path(registry_path).read_text())
    out_root_p = Path(out_root)
    index_items = []

    for item in reg["items"]:
        slug, title, ticker = item["slug"], item["title"], item["ticker"]
        df = read_csv(ticker)
        df = df.sort_values("date")
        series = [{"date": d.strftime("%Y-%m-%d"), "value": float(c)} for d, c in zip(df["date"], df["close"])]
        slug_dir = out_root_p / slug
        slug_dir.mkdir(parents=True, exist_ok=True)

        (slug_dir / "series.json").write_text(json.dumps({"slug": slug, "series": series}))
        (slug_dir / "meta.json").write_text(json.dumps({
            "slug": slug, "title": title, "ticker": ticker,
            "first_date": series[0]["date"] if series else None,
            "last_date": series[-1]["date"] if series else None,
            "description": item.get("description","")
        }))
        index_items.append({"slug": slug, "title": title, "url": f"/portfolios/{slug}/"})

    (out_root_p / "index.json").write_text(json.dumps({"items": index_items}))
