from typing import Dict, List, Optional

import pandas as pd


class Stock:
    def __init__(self, stock_data: pd.DataFrame) -> None:
        self.stock_data = stock_data
        self.ticker: Optional[str] = None
        self.period: Optional[str] = None
        self.interval: Optional[str] = None
        self.atr: Optional[pd.Series] = None
        self.zones: Optional[List[Dict]] = None

