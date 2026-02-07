import pandas as pd

from models.stock import Stock


def add_atr(stock: Stock, window: int = 14) -> None:
    if window <= 0:
        raise ValueError("window must be a positive integer")

    df = stock.stock_data
    for col in ("High", "Low", "Close"):
        if col not in df.columns:
            raise ValueError(f"column '{col}' not found in stock data")

    high_low = df["High"] - df["Low"]
    high_close_prev = (df["High"] - df["Close"].shift(1)).abs()
    low_close_prev = (df["Low"] - df["Close"].shift(1)).abs()

    true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
    stock.atr = true_range.rolling(window=window).mean()
