import numpy as np

from models.stock import Stock


def find_pivot_points(stock: Stock, window: int = 3) -> None:
    """
    Find pivot high/low points in stock data.

    Args:
        stock: Stock object containing OHLC data with 'High' and 'Low'.
        window: Number of candles on each side to confirm a pivot.
            Lower = more sensitive (detects more pivots).
    """
    highs = stock.stock_data['High'].values
    lows = stock.stock_data['Low'].values
    pivot_highs = [np.nan] * len(stock.stock_data)
    pivot_lows = [np.nan] * len(stock.stock_data)

    for i in range(window, len(stock.stock_data) - window):
        # Pivot High: current high greater than surrounding highs
        if highs[i] == max(highs[i - window:i + window + 1]):
            pivot_highs[i] = highs[i]

        # Pivot Low: current low lower than surrounding lows
        if lows[i] == min(lows[i - window:i + window + 1]):
            pivot_lows[i] = lows[i]

    stock.stock_data['Pivot_High'] = pivot_highs
    stock.stock_data['Pivot_Low'] = pivot_lows
