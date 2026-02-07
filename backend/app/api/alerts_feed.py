import logging

from fastapi import APIRouter, HTTPException, Query

from app.config import settings
from app.schemas.alerts import AlertFeedItem
from app.services.charting.pipeline import (
    ensure_trigger_chart,
    get_trigger_chart_url,
    has_trigger_chart,
)
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/alerts", tags=["alerts"])
logger = logging.getLogger(__name__)


@router.get("/feed", response_model=list[AlertFeedItem])
def get_alerts_feed(
    limit: int = Query(default=20, ge=1, le=200),
    cursor: str | None = Query(default=None),
    q: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
) -> list[AlertFeedItem]:
    try:
        items = supabase_service.list_unlinked_alert_triggers(
            limit=limit,
            cursor=cursor,
            q=q,
            symbol=symbol,
            alert_type=alert_type,
        )
        generation_attempts = 0
        for item in items:
            try:
                if has_trigger_chart(item, profile="alert_basic"):
                    item.chart_url = get_trigger_chart_url(item, profile="alert_basic")
                    continue

                if generation_attempts >= settings.max_new_charts_per_feed_request:
                    item.chart_url = None
                    continue

                generation_attempts += 1
                item.chart_url = ensure_trigger_chart(item, profile="alert_basic")
            except Exception:  # noqa: BLE001
                logger.exception(
                    "Chart generation failed for trigger_id=%s", item.trigger_id
                )
                item.chart_url = None
        return items
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
