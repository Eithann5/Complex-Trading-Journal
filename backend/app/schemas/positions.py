from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class TriggerLinkRequest(BaseModel):
    position_id: str
    link_type: Literal["trigger", "context", "post_entry"]


class OkResponse(BaseModel):
    ok: bool


class PositionPatchRequest(BaseModel):
    origin: Literal["manual", "alert_based"] | None = None
    notes: str | None = None
    open_time_utc: datetime | None = None


class PositionTagCreateRequest(BaseModel):
    tag: str
    source: Literal["manual", "auto"] = "manual"


class PositionTagItem(BaseModel):
    id: str
    tag: str
    source: str
    created_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class LinkedTriggerItem(BaseModel):
    trigger_id: str
    link_type: str
    linked_at_utc: datetime

    model_config = ConfigDict(from_attributes=True)


class OpenPositionItem(BaseModel):
    id: str
    ticker: str
    status: str
    origin: str
    notes: str | None
    open_time_utc: datetime | None
    close_time_utc: datetime | None
    created_at_utc: datetime
    last: float | None = None
    position: float | None = None
    mkt_value: float | None = None
    chg_pct: float | None = None
    pnl: float | None = None
    unrealized_pnl: float | None = None
    unrealized_pnl_pct: float | None = None
    currency: str | None = None
    tags: list[PositionTagItem]
    linked_triggers: list[LinkedTriggerItem]

    model_config = ConfigDict(from_attributes=True)


class SnapshotRunResponse(BaseModel):
    ok: bool
    snapshots_created: int
    tickers: list[str]
    snapshot_time_utc: datetime
