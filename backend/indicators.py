from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd

from .store import read_csv
OUT_DIR = Path("public/data/indicators")

def _series_from_store(a: str, b: str) -> pd.DataFrame:
    da = read_csv(a)
    db = read_csv(b)
    if da.empty or db.empty:
        return pd.DataFrame(columns=["date","a","b","ratio"])
    df = pd.merge(da, db, on="date", suffixes=("_a","_b"))
    df = df.rename(columns={"close_a":"a","close_b":"b"})
    df["ratio"] = df["a"] / df["b"]
    return df.dropna().sort_values("date")

def _emit_json(p: Path, obj: Any) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False))

def build_indicators(registry_path: str, out_root: str = str(OUT_DIR)) -> None:
    reg = json.loads(Path(registry_path).read_text())
    out_root_p = Path(out_root)
    index_items: List[Dict[str, Any]] = []

    for item in reg["items"]:
        slug, title, a, b, desc = item["slug"], item["title"], item["a"], item["b"], item.get("description","")
        df = _series_from_store(a, b)
        slug_dir = out_root_p / slug

        # series.json
        series = {
            "slug": slug,
            "series": [
                {"date": d.strftime("%Y-%m-%d"), "a": float(row.a), "b": float(row.b), "ratio": float(row.ratio)}
                for d, row in df.set_index("date").iterrows()
            ]
        }
        _emit_json(slug_dir / "series.json", series)

        # series_me.json (month-end)
        if not df.empty:
            me = df.set_index("date").resample("ME").last().reset_index()
            series_me = {
                "slug": slug,
                "series": [
                    {"date": d.strftime("%Y-%m-%d"), "a": float(row.a), "b": float(row.b), "ratio": float(row.ratio)}
                    for d, row in me.set_index("date").iterrows()
                ]
            }
        else:
            series_me = {"slug": slug, "series": []}
        _emit_json(slug_dir / "series_me.json", series_me)

        # meta.json
        meta = {
            "slug": slug,
            "title": title,
            "a": a, "b": b,
            "description": desc,
            "first_date": series["series"][0]["date"] if series["series"] else None,
            "last_date": series["series"][-1]["date"] if series["series"] else None
        }
        _emit_json(slug_dir / "meta.json", meta)

        index_items.append({"slug": slug, "title": title, "url": f"/indicators/{slug}/"})

    _emit_json(out_root_p / "index.json", {"items": index_items})
