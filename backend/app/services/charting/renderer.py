import sys
import time
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from app.services.charting.profiles import ChartProfile
from app.config import settings

VENDOR_SAMI_ROOT = Path(__file__).resolve().parent / "vendor" / "sami"
_OHLC_CACHE: dict[tuple[str, str, str], tuple[float, pd.DataFrame]] = {}
_LAST_FETCH_MONOTONIC: float | None = None


def _add_vendor_path() -> None:
    vendor_path = str(VENDOR_SAMI_ROOT)
    if vendor_path not in sys.path:
        sys.path.insert(0, vendor_path)


def _load_vendor_components() -> tuple[Any, Any, Any]:
    _add_vendor_path()
    from enrichments.sma import add_sma  # type: ignore
    from input.fetch_ticker_data import get_ticker_historical_data  # type: ignore
    from models.stock import Stock  # type: ignore

    return get_ticker_historical_data, Stock, add_sma


def _build_addplots(df: pd.DataFrame, indicators: tuple[str, ...]) -> list[Any]:
    addplots: list[Any] = []
    color_by_window = {20: "#1f77b4", 150: "#ff1493", 200: "#d62728"}
    for indicator in indicators:
        if not indicator.startswith("sma_"):
            continue
        try:
            window = int(indicator.split("_", maxsplit=1)[1])
        except (IndexError, ValueError):
            continue
        column = f"SMA_{window}"
        if column in df.columns:
            series = df[column]
            if series.dropna().empty:
                continue
            addplots.append(
                mpf.make_addplot(
                    series,
                    color=color_by_window.get(window, "#444444"),
                    width=1.2,
                    label=f"SMA {window}",
                )
            )
    return addplots


def _prepare_ohlc_frame(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.index, pd.DatetimeIndex):
        return df
    if "Date" not in df.columns:
        raise ValueError("Expected 'Date' column in stock data")
    framed = df.copy()
    framed["Date"] = pd.to_datetime(framed["Date"], utc=True)
    return framed.set_index("Date")


def _get_cached_ohlc(
    *,
    symbol: str,
    period: str,
    interval: str,
    fetch_fn: Any,
) -> pd.DataFrame:
    global _LAST_FETCH_MONOTONIC
    cache_key = (symbol, period, interval)
    now = time.monotonic()
    cached_entry = _OHLC_CACHE.get(cache_key)
    if cached_entry is not None:
        cached_at, cached_df = cached_entry
        if now - cached_at <= settings.chart_ohlc_cache_ttl_seconds:
            return cached_df.copy(deep=True)

    if _LAST_FETCH_MONOTONIC is not None:
        elapsed = now - _LAST_FETCH_MONOTONIC
        sleep_seconds = settings.chart_fetch_min_interval_seconds - elapsed
        if sleep_seconds > 0:
            time.sleep(sleep_seconds)

    fetched_df = fetch_fn(symbol, period, interval)
    _LAST_FETCH_MONOTONIC = time.monotonic()
    _OHLC_CACHE[cache_key] = (_LAST_FETCH_MONOTONIC, fetched_df)
    return fetched_df.copy(deep=True)


def render_trigger_chart(trigger: Any, profile: ChartProfile, output_path: Path) -> None:
    get_ticker_historical_data, Stock, add_sma = _load_vendor_components()
    symbol = str(trigger.symbol).upper().strip()
    raw_df = _get_cached_ohlc(
        symbol=symbol,
        period=profile.data_period,
        interval=profile.data_interval,
        fetch_fn=get_ticker_historical_data,
    )
    stock = Stock(raw_df)
    stock.ticker = symbol

    for indicator in profile.indicators:
        if indicator.startswith("sma_"):
            window = int(indicator.split("_", maxsplit=1)[1])
            add_sma(stock, window)

    df = _prepare_ohlc_frame(stock.stock_data)
    if profile.lookback_days > 0 and len(df) > profile.lookback_days:
        df = df.tail(profile.lookback_days).copy()
    addplots = _build_addplots(df, profile.indicators)

    fig, _axes = mpf.plot(
        df,
        type="candle",
        style="yahoo",
        addplot=addplots if addplots else None,
        volume=profile.render.show_volume,
        returnfig=True,
        figsize=profile.render.figsize,
    )

    if profile.render.tight_layout:
        fig.tight_layout(pad=0.2)

    fig.savefig(output_path, dpi=profile.render.dpi, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)
