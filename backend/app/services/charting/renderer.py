import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd

from app.services.charting.profiles import ChartProfile

VENDOR_SAMI_ROOT = Path(__file__).resolve().parent / "vendor" / "sami"


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
            addplots.append(
                mpf.make_addplot(
                    df[column],
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


def _render_fallback_chart(symbol: str, profile: ChartProfile, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=profile.render.figsize)
    ax.set_axis_off()
    ax.text(
        0.5,
        0.55,
        symbol,
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
    )
    ax.text(
        0.5,
        0.42,
        "Chart data unavailable",
        ha="center",
        va="center",
        fontsize=11,
        color="#666666",
    )
    if profile.render.tight_layout:
        fig.tight_layout(pad=0.2)
    fig.savefig(output_path, dpi=profile.render.dpi, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


def render_trigger_chart(trigger: Any, profile: ChartProfile, output_path: Path) -> None:
    get_ticker_historical_data, Stock, add_sma = _load_vendor_components()
    symbol = str(trigger.symbol).upper().strip()
    try:
        raw_df = get_ticker_historical_data(
            symbol, profile.data_period, profile.data_interval
        )
        stock = Stock(raw_df)
        stock.ticker = symbol

        for indicator in profile.indicators:
            if indicator.startswith("sma_"):
                window = int(indicator.split("_", maxsplit=1)[1])
                add_sma(stock, window)

        df = _prepare_ohlc_frame(stock.stock_data)
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
    except Exception:  # noqa: BLE001
        _render_fallback_chart(symbol, profile, output_path)
