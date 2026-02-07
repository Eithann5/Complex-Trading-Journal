from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AlertFeedItem(BaseModel):
    trigger_id: str
    alert_id: str | None
    symbol: str
    alert_type: str
    triggered_at_utc: datetime
    price: float | None
    message: str | None
    condition: dict[str, Any]
    snapshot: dict[str, Any]
    chart_url: str | None = None

    model_config = ConfigDict(from_attributes=True)
