import pandas as pd

from models.stock import Stock


def add_sma(stock: Stock, window: int, column: str = "Close") -> None:
    if window <= 0:
        raise ValueError("window must be a positive integer")
    if column not in stock.stock_data.columns:
        raise ValueError(f"column '{column}' not found in stock data")

    target_col = f"SMA_{window}"
    stock.stock_data[target_col] = (
        pd.Series(stock.stock_data[column]).rolling(window=window).mean()
    )
