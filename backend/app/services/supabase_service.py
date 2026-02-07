import json
from datetime import datetime
from typing import Any

from postgrest.exceptions import APIError
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from app.config import settings
from app.schemas.alerts import AlertFeedItem


def _parse_json_object(raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def _parse_cursor(cursor: str) -> tuple[str, str]:
    parts = cursor.split("|", maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        raise ValueError("Invalid cursor format")
    return parts[0], parts[1]


class SupabaseService:
    def __init__(self) -> None:
        self._client: Client | None = None

    def _get_client(self) -> Client:
        if self._client is not None:
            return self._client
        if not settings.supabase_url or not settings.supabase_service_role_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")
        self._client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
            options=ClientOptions(schema=settings.supabase_schema),
        )
        return self._client

    def list_unlinked_alert_triggers(
        self,
        *,
        limit: int = 20,
        cursor: str | None = None,
        q: str | None = None,
        symbol: str | None = None,
        alert_type: str | None = None,
    ) -> list[AlertFeedItem]:
        client = self._get_client()
        select_columns = "id,alert_id,symbol,alert_type,triggered_at,price,message,condition,snapshot"
        query = client.table("alerts_triggers").select(select_columns)
        query = query.order("triggered_at", desc=True).order("id", desc=True)

        linked_ids: list[str] = []
        try:
            linked_rows = (
                client.table("trigger_position_links").select("trigger_id").execute().data or []
            )
            linked_ids = [row["trigger_id"] for row in linked_rows if row.get("trigger_id")]
        except APIError:
            linked_ids = []
        if linked_ids:
            query = query.not_.in_("id", linked_ids)

        if cursor:
            cursor_time, cursor_id = _parse_cursor(cursor)
            query = query.or_(
                f"triggered_at.lt.{cursor_time},"
                f"and(triggered_at.eq.{cursor_time},id.lt.{cursor_id})"
            )

        if q:
            q_value = q.strip()
            if q_value:
                query = query.or_(
                    f"symbol.ilike.%{q_value}%,alert_type.ilike.%{q_value}%"
                )

        if symbol:
            query = query.eq("symbol", symbol.strip())
        if alert_type:
            query = query.eq("alert_type", alert_type.strip())

        result = query.limit(limit).execute()

        items: list[AlertFeedItem] = []
        for row in result.data or []:
            items.append(
                AlertFeedItem(
                    trigger_id=row["id"],
                    alert_id=row.get("alert_id"),
                    symbol=row["symbol"],
                    alert_type=row["alert_type"],
                    triggered_at_utc=datetime.fromisoformat(
                        row["triggered_at"].replace("Z", "+00:00")
                    ),
                    price=float(row["price"]) if row.get("price") is not None else None,
                    message=row.get("message"),
                    condition=_parse_json_object(row.get("condition")),
                    snapshot=_parse_json_object(row.get("snapshot")),
                    chart_url=None,
                )
            )

        return items


supabase_service = SupabaseService()
