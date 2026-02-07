# Mission 004 — Chart infrastructure using existing `sami` engine

## Read first
- Read `AGENTS.md` and follow it strictly.
- Charts are static PNG images.
- Charts are served by backend via `/static`.
- No external uploads (no S3 / no Supabase Storage).
- Never overwrite existing chart images.

---

## Goal
Integrate the existing local charting/algorithm repository **`sami`**
into the backend and build a **chart generation infrastructure** that:

- selects which algorithms to run via chart profiles
- generates deterministic PNG images
- caches images on disk
- exposes them via URL
- supports **basic alert charts now** and **advanced position charts later**

Mission 004 is about **infrastructure**, not inventing new chart logic.

---

## Source of chart logic (IMPORTANT)

The chart logic already exists locally at:

```
C:\Users\Eitan\PycharmProjects\sami
```

This code:
- fetches OHLC data
- computes indicators (SMA, ATR, zones, pivots, etc.)
- renders candlestick charts via matplotlib

### Requirement
- Vendor-copy the required parts of this repo into the backend.
- The backend must NOT depend on the external path at runtime.

---

## Vendor-copy rules

Copy the following directories from the local `sami` repo into:

```
backend/app/services/charting/vendor/sami/
```

Directories to copy:
- `input/`
- `enrichments/`
- `models/`
- `output/`

Do NOT:
- rewrite or refactor the vendored code
- change algorithms inside vendored files unless absolutely required

Website-specific behavior must live **outside** the vendored code.

---

## Chart profiles

Charts are generated using **profiles** that define:
- lookback window
- which algorithms run
- render settings
- output location

### Profile: `alert_basic` (IMPLEMENT NOW)

Used for the Alerts Feed.

**Data**
- Timeframe: daily
- Lookback: ~60 candles (≈ 2 months)

**Indicators**
- SMA 20
- SMA 150
- SMA 200

**Visual rules**
- NO title/header on the chart
- Smaller figure size (card-friendly)
- Tight margins
- No zones
- No pivots
- Minimal legend

**Output path**
```
data/charts/triggers/{symbol}/{trigger_id}_alert_basic_v1.png
```

---

### Profile: `position_advanced` (STUB ONLY)

Do NOT implement rendering yet.

Reserve infrastructure only.

**Planned behavior**
- Lookback: ~252 candles (1 year)
- Indicators: zones, pivots, ATR, trend logic
- Larger figure
- Used on Positions page

**Reserved output path**
```
data/charts/positions/{position_id}_position_advanced_v1.png
```

---

## Backend charting infrastructure

Create the following modules:

```
backend/app/services/charting/
├── profiles.py
├── cache.py
├── pipeline.py
├── renderer.py
└── vendor/
    └── sami/
```

---

### profiles.py
Define profile configurations.

Each profile must specify:
- profile name
- lookback_days
- indicators to run
- output subdirectory
- filename suffix
- render options (size, title on/off)

---

### renderer.py (CRITICAL)

Implement a **website-specific renderer wrapper** that:

1. Uses vendored `sami` code to:
   - fetch OHLC data
   - compute indicators (SMA only for `alert_basic`)
2. Renders charts using matplotlib:
   - NO title/header
   - card-friendly size (e.g. ~1200x600)
   - tight layout
3. Saves the PNG to the exact output path passed in

Do NOT:
- call `sami.output.visualizer.save_candlestick_chart` directly if it forces titles
- add new indicators
- reimplement indicator logic

The renderer must expose:

```python
render_trigger_chart(trigger, profile, output_path) -> None
```

---

### cache.py
Responsible for:
- computing deterministic output paths
- creating directories if missing
- checking for existing files
- enforcing **no overwrite**

---

### pipeline.py
Expose:

```python
ensure_trigger_chart(trigger, profile="alert_basic") -> str
```

Behavior:
- resolve output path via cache
- if file exists → return URL
- if missing → call renderer → return URL

---

## Alerts feed integration

Update:

```
GET /api/alerts/feed
```

So that for each trigger:
- `ensure_trigger_chart(trigger, profile="alert_basic")` is called
- response includes:

```json
"chart_url": "/static/charts/triggers/{symbol}/{trigger_id}_alert_basic_v1.png"
```

---

## Static URL rules

The backend serves repo-root `data/` at `/static`.

Therefore:
```
data/charts/...  →  /static/charts/...
```

---

## Acceptance criteria

1. Calling `GET /api/alerts/feed` returns `chart_url` for each item
2. Opening `chart_url` in browser:
   - loads a PNG
   - has NO title/header
   - fits cleanly in a feed card
3. Calling the feed twice:
   - does NOT regenerate images
4. Code structure allows adding `position_advanced` without refactor

---

## Deliverables
- Vendored `sami` code in backend
- Charting infrastructure modules
- Updated alerts feed endpoint
- Notes explaining:
  - profile selection
  - where images are stored
  - how caching works
