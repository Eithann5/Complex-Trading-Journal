import yfinance as yf
import pandas as pd


def get_ticker_historical_data(
    ticker: str,
    period: str,
    interval: str,
) -> pd.DataFrame:
    """
    Fetch historical stock data using yfinance and return a pandas DataFrame.

    :param ticker: Stock symbol, e.g., 'FTNT'
    :param period: Duration of historical data, e.g., '1y'
    :param interval: Data frequency, e.g., '1d'
    :return: pandas DataFrame with historical stock data
    """
    print(f"Fetching data for {ticker} | Period: {period}, Interval: {interval}")
    stock = yf.Ticker(ticker)

    data = stock.history(period=period, interval=interval)
    if not data.empty:
        data = data.drop(columns=["Dividends", "Stock Splits"])
        return data.reset_index()
    else:
        raise ValueError(f"No data found for {ticker} with period={period} and interval={interval}")
