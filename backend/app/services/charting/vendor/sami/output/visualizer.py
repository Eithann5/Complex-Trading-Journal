import os
from typing import List, Dict

import numpy as np
import pandas as pd
import mplfinance as mpf
from matplotlib.patches import Rectangle

from models.stock import Stock

# ---------- HARD-CODED LOOK & FEEL ----------
STYLE = "yahoo"
RESULTS_DIR = "results"

FIGSIZE = (20, 10)  # big chart
DPI = 300
TITLE_FONT = 12
TITLE_Y = 0.92  # minimal padding
SHOW_VOLUME = True

# MAs: use columns named exactly as below (create them beforehand).
MA_WINDOWS = [20, 150, 200]
MA_COLORS = {20: "blue", 150: "#ff1493", 200: "red"}   # marker pink for 150
MA_WIDTH = 1.6

# Pivots: plot if columns exist
PIVOT_MARKER_SIZE = 21        # a bit smaller so they don't dominate
PIVOT_HIGH_COLOR = "red"
PIVOT_LOW_COLOR = "lime"

# Zones (rectangles)
ZONE_COLOR = "#f4b183"  # warm sand
ZONE_ALPHA = 0.3     # slightly lighter
ZONE_ZORDER = 0         # behind candles

def _make_ma_addplots(df: pd.DataFrame) -> List:
    """Addplots for SMA_20 / SMA_150 / SMA_200 if present (hard-coded)."""
    addplots = []
    for w in MA_WINDOWS:
        col = f"SMA_{w}"
        if col in df.columns:
            addplots.append(
                mpf.make_addplot(
                    df[col],
                    color=MA_COLORS[w],
                    width=MA_WIDTH,
                    label=f"SMA {w}",
                )
            )
    return addplots


def _make_pivot_addplots(df: pd.DataFrame) -> List:
    """Addplots for pivot highs/lows if columns exist (hard-coded)."""
    addplots = []
    if "Pivot_High" in df.columns:
        addplots.append(
            mpf.make_addplot(
                df["Pivot_High"],
                type="scatter",
                marker="^",
                markersize=PIVOT_MARKER_SIZE,
                color=PIVOT_HIGH_COLOR,
            )
        )
    if "Pivot_Low" in df.columns:
        addplots.append(
            mpf.make_addplot(
                df["Pivot_Low"],
                type="scatter",
                marker="v",
                markersize=PIVOT_MARKER_SIZE,
                color=PIVOT_LOW_COLOR,
            )
        )
    return addplots


def _add_zone_patches(axes, df: pd.DataFrame, zones: List[Dict]) -> None:
    """
    Draw semi-transparent rectangles for zones.
    Opacity scales with zone strength (pivot_count).
    Zones must be a list of dicts with:
      start_index, end_index (int or Timestamp), low_price, high_price, pivot_count
    """
    if not zones:
        return

    ax_main = axes[0] if isinstance(axes, (list, tuple)) else axes

    # normalize pivot_count for alpha scaling
    counts = [z.get("pivot_count", 1) for z in zones]
    min_c, max_c = min(counts), max(counts)
    denom = max(1, max_c - min_c)

    for z in zones:
        s = z["start_index"]
        e = z["end_index"]

        # map timestamps to integer x positions (works for datetime or integer index)
        start_pos = df.index.get_loc(s) if not isinstance(s, int) else s
        end_pos = df.index.get_loc(e) if not isinstance(e, int) else e
        if end_pos < start_pos:
            start_pos, end_pos = end_pos, start_pos

        width = end_pos - start_pos + 1
        height = z["high_price"] - z["low_price"]
        if width <= 0 or height <= 0:
            continue

        # scale alpha: weak zones ~0.15, strong zones ~0.5
        pivots = z.get("pivot_count", 1)
        strength = (pivots - min_c) / denom
        alpha = 0.5 + 0.25 * strength

        rect = Rectangle(
            (start_pos, z["low_price"]),
            width,
            height,
            facecolor="#b388eb",    # light purple fill
            edgecolor="#6a0dad",    # strong purple border
            linewidth=0.8,          # subtle border thickness
            alpha=alpha,            # transparency applies to fill
            zorder=ZONE_ZORDER,
        )
        ax_main.add_patch(rect)


def save_candlestick_chart(
    stock: Stock,
    zones: List[Dict] | None = None,
    out_dir: str = RESULTS_DIR,
) -> str:
    """
    HARD-CODED renderer:
      - Candles + Volume (volume panel smaller via panel_ratios)
      - SMA 20/150/200 (blue / deep pink / red) if columns exist
      - Pivot markers if Pivot_High / Pivot_Low columns exist
      - Zones as semi-transparent rectangles (if provided)
      - Trendlines (same color for all; dashed if broken)
      - Locks Y limits to data range with small padding to avoid autoscale blow-ups.

    Saves PNG to results folder and returns the path.
    """
    df = stock.stock_data
    ticker = stock.ticker or "UNKNOWN"
    if zones is None:
        zones = stock.zones

    if not isinstance(df.index, pd.DatetimeIndex):
        if "Date" in df.columns:
            df = df.copy()
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        else:
            raise TypeError("Expected stock_data index to be DatetimeIndex or to have a 'Date' column.")

    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{ticker.upper()}.png")

    addplots: List = []
    addplots += _make_ma_addplots(df)
    addplots += _make_pivot_addplots(df)

    # Plot once; then draw zone rectangles and lock y-limits
    fig, axes = mpf.plot(
        df,
        type="candle",
        style=STYLE,
        addplot=addplots if addplots else None,
        volume=SHOW_VOLUME,
        returnfig=True,
        figsize=FIGSIZE,
        title=dict(title=f"{ticker.upper()} Candlestick Chart", fontsize=TITLE_FONT, y=TITLE_Y),
        panel_ratios=(4, 1)  # Price 4x taller than volume
    )

    # Price axis handle
    ax_main = axes[0] if isinstance(axes, (list, tuple)) else axes

    # Add zones behind candles
    if zones:
        _add_zone_patches(axes, df, zones)

    # --- Clamp y-limits to data range (with small padding) to avoid 0..200 explosions ---
    data_low = float(np.nanmin(df["Low"].to_numpy()))
    data_high = float(np.nanmax(df["High"].to_numpy()))
    if np.isfinite(data_low) and np.isfinite(data_high) and data_high > data_low:
        pad = 0.02  # 2% padding
        ymin = data_low * (1.0 - pad)
        ymax = data_high * (1.0 + pad)
        ax_main.set_ylim(ymin, ymax)
        ax_main.set_autoscaley_on(False)  # lock it in

    fig.savefig(out_path, dpi=DPI, bbox_inches="tight")
    fig.clf()
    return out_path
