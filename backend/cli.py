from __future__ import annotations
import json
from pathlib import Path
import typer
import pandas as pd
from rich import print as rprint

from .yahoo_proxy import fetch_chart
from .store import upsert_prices
from .indicators import build_indicators
from .portfolios import build_portfolios

app = typer.Typer(help="InvestLog backend CLI")

def _iter_indicator_tickers(registry_path: str):
    reg = json.loads(Path(registry_path).read_text())
    for it in reg["items"]:
        yield it["a"]; yield it["b"]

def _iter_portfolio_tickers(registry_path: str):
    reg = json.loads(Path(registry_path).read_text())
    for it in reg["items"]:
        if "ticker" in it: yield it["ticker"]

@app.command("sync-indicator-tickers")
def sync_indicator_tickers(
    registry: str = typer.Option(..., help="data/indicators/registry.json"),
):
    tickers = sorted(set(_iter_indicator_tickers(registry)))
    for t in tickers:
        chart = fetch_chart(t, interval="1d", range_="max")
        res = chart.get("chart", {}).get("result", [])
        if not res:
            rprint(f"[red]No result for {t}[/red]")
            continue
        r = res[0]
        ts = r.get("timestamp", [])
        closes = r.get("indicators", {}).get("quote", [{}])[0].get("close", [])
        if not ts or not closes:
            rprint(f"[red]Empty data for {t}[/red]")
            continue
        upsert_prices(t, ts, closes)
        rprint(f"[green]Synced {t}[/green]")

@app.command("build-indicators")
def build_ind(
    registry: str = typer.Option(..., help="data/indicators/registry.json"),
    out: str = typer.Option("public/data/indicators", help="Output dir"),
):
    build_indicators(registry, out)
    rprint(f"[green]Indicators built → {out}[/green]")

@app.command("build-portfolios")
def build_port(
    registry: str = typer.Option(..., help="data/portfolios/registry.json"),
    out: str = typer.Option("public/data/portfolios", help="Output dir"),
):
    build_portfolios(registry, out)
    rprint(f"[green]Portfolios built → {out}[/green]")

@app.command("build-all")
def build_all(
    ind_reg: str = typer.Option("data/indicators/registry.json",
                                help="Indicators registry"),
    port_reg: str = typer.Option("data/portfolios/registry.json",
                                 help="Portfolios registry"),
):
    sync_indicator_tickers(ind_reg)
    build_indicators(ind_reg, "public/data/indicators")
    build_portfolios(port_reg, "public/data/portfolios")
    rprint("[cyan]All done.[/cyan]")

if __name__ == "__main__":
    app()
