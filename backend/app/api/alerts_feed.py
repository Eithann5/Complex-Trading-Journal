from fastapi import APIRouter, HTTPException, Query

from app.schemas.alerts import AlertFeedItem
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/feed", response_model=list[AlertFeedItem])
def get_alerts_feed(
    limit: int = Query(default=20, ge=1, le=200),
    cursor: str | None = Query(default=None),
    q: str | None = Query(default=None),
    symbol: str | None = Query(default=None),
    alert_type: str | None = Query(default=None),
) -> list[AlertFeedItem]:
    try:
        return supabase_service.list_unlinked_alert_triggers(
            limit=limit,
            cursor=cursor,
            q=q,
            symbol=symbol,
            alert_type=alert_type,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
