# InvestLog Tools (Astro + AdminLTE v4 RC3)

- **SSR/SSG** hubs (no client fetch). Detail pages may use client JS only for interactivity; data lives in `public/data/**`.
- **Data pipeline**: GitHub Action runs nightly, fetches prices via **PHP proxy**, stores per-ticker CSV in `data/store/tickers/`, emits JSON under `public/data/**`.

## Dev
- `npm i`
- `npm run dev`

## Data
- `pip install -r requirements.txt`
- `python -m backend.cli build-all --ind-reg data/indicators/registry.json --port-reg data/portfolios/registry.json`
