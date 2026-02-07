import json
from datetime import datetime
from typing import Any

from postgrest.exceptions import APIError
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from app.config import settings
from app.schemas.alerts import AlertFeedItem
from app.schemas.positions import (
    LinkedTriggerItem,
    OpenPositionItem,
    PositionTagItem,
)


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

    def link_trigger_to_position(
        self,
        *,
        trigger_id: str,
        position_id: str,
        link_type: str,
    ) -> None:
        payload = {
            "trigger_id": trigger_id,
            "position_id": position_id,
            "link_type": link_type,
            "created_by": "api",
        }
        self._get_client().table("trigger_position_links").insert(payload).execute()

    def list_open_positions(self) -> list[OpenPositionItem]:
        client = self._get_client()
        positions_rows = (
            client.table("position_journal")
            .select("id,ticker,status,open_time_utc,close_time_utc,origin,notes,created_at")
            .eq("status", "open")
            .order("created_at", desc=True)
            .execute()
            .data
            or []
        )
        if not positions_rows:
            return []

        tickers = sorted({str(row["ticker"]).upper() for row in positions_rows})
        latest_snapshot_by_ticker = self._get_latest_snapshot_by_ticker(tickers)

        position_ids = [row["id"] for row in positions_rows]
        tags_rows = (
            client.table("position_tags")
            .select("id,position_id,tag,source,created_at")
            .in_("position_id", position_ids)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )
        links_rows = (
            client.table("trigger_position_links")
            .select("position_id,trigger_id,link_type,created_at")
            .in_("position_id", position_ids)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )

        tags_by_position: dict[str, list[PositionTagItem]] = {
            position_id: [] for position_id in position_ids
        }
        for row in tags_rows:
            tags_by_position[row["position_id"]].append(
                PositionTagItem(
                    id=row["id"],
                    tag=row["tag"],
                    source=row["source"],
                    created_at_utc=datetime.fromisoformat(
                        row["created_at"].replace("Z", "+00:00")
                    ),
                )
            )

        links_by_position: dict[str, list[LinkedTriggerItem]] = {
            position_id: [] for position_id in position_ids
        }
        for row in links_rows:
            links_by_position[row["position_id"]].append(
                LinkedTriggerItem(
                    trigger_id=row["trigger_id"],
                    link_type=row["link_type"],
                    linked_at_utc=datetime.fromisoformat(
                        row["created_at"].replace("Z", "+00:00")
                    ),
                )
            )

        items: list[OpenPositionItem] = []
        for row in positions_rows:
            ticker = str(row["ticker"]).upper()
            snapshot = latest_snapshot_by_ticker.get(ticker)
            quantity = float(snapshot["quantity"]) if snapshot and snapshot.get("quantity") is not None else None
            market_price = (
                float(snapshot["market_price"])
                if snapshot and snapshot.get("market_price") is not None
                else None
            )
            avg_cost = (
                float(snapshot["avg_cost"])
                if snapshot and snapshot.get("avg_cost") is not None
                else None
            )
            unrealized_pnl = (
                float(snapshot["unrealized_pnl"])
                if snapshot and snapshot.get("unrealized_pnl") is not None
                else None
            )
            mkt_value = quantity * market_price if quantity is not None and market_price is not None else None
            cost_basis = quantity * avg_cost if quantity is not None and avg_cost is not None else None
            unrealized_pnl_pct = (
                (unrealized_pnl / abs(cost_basis) * 100)
                if unrealized_pnl is not None and cost_basis not in (None, 0)
                else None
            )
            raw = snapshot.get("raw") if snapshot else {}
            chg_pct = (
                float(raw.get("chgPercent"))
                if isinstance(raw, dict) and raw.get("chgPercent") is not None
                else None
            )
            pnl = (
                float(raw.get("dailyPnl"))
                if isinstance(raw, dict) and raw.get("dailyPnl") is not None
                else None
            )
            items.append(
                OpenPositionItem(
                    id=row["id"],
                    ticker=ticker,
                    status=row["status"],
                    origin=row["origin"],
                    notes=row.get("notes"),
                    open_time_utc=datetime.fromisoformat(
                        row["open_time_utc"].replace("Z", "+00:00")
                    )
                    if row.get("open_time_utc")
                    else None,
                    close_time_utc=datetime.fromisoformat(
                        row["close_time_utc"].replace("Z", "+00:00")
                    )
                    if row.get("close_time_utc")
                    else None,
                    created_at_utc=datetime.fromisoformat(
                        row["created_at"].replace("Z", "+00:00")
                    ),
                    last=market_price,
                    position=quantity,
                    mkt_value=mkt_value,
                    chg_pct=chg_pct,
                    pnl=pnl,
                    unrealized_pnl=unrealized_pnl,
                    unrealized_pnl_pct=unrealized_pnl_pct,
                    currency=snapshot.get("currency") if snapshot else None,
                    tags=tags_by_position.get(row["id"], []),
                    linked_triggers=links_by_position.get(row["id"], []),
                )
            )
        return items

    def update_position(
        self, position_id: str, updates: dict[str, Any]
    ) -> OpenPositionItem:
        payload = updates.copy()
        if isinstance(payload.get("open_time_utc"), datetime):
            payload["open_time_utc"] = payload["open_time_utc"].isoformat()

        client = self._get_client()
        updated_rows = (
            client.table("position_journal")
            .update(payload)
            .eq("id", position_id)
            .select("id,ticker,status,open_time_utc,close_time_utc,origin,notes,created_at")
            .limit(1)
            .execute()
            .data
            or []
        )
        if not updated_rows:
            raise ValueError("Position not found")

        row = updated_rows[0]
        return OpenPositionItem(
            id=row["id"],
            ticker=row["ticker"],
            status=row["status"],
            origin=row["origin"],
            notes=row.get("notes"),
            open_time_utc=datetime.fromisoformat(
                row["open_time_utc"].replace("Z", "+00:00")
            )
            if row.get("open_time_utc")
            else None,
            close_time_utc=datetime.fromisoformat(
                row["close_time_utc"].replace("Z", "+00:00")
            )
            if row.get("close_time_utc")
            else None,
            created_at_utc=datetime.fromisoformat(
                row["created_at"].replace("Z", "+00:00")
            ),
            last=None,
            position=None,
            mkt_value=None,
            chg_pct=None,
            pnl=None,
            unrealized_pnl=None,
            unrealized_pnl_pct=None,
            currency=None,
            tags=self._get_position_tags(position_id),
            linked_triggers=self._get_position_links(position_id),
        )

    def _get_latest_snapshot_by_ticker(self, tickers: list[str]) -> dict[str, dict[str, Any]]:
        if not tickers:
            return {}
        try:
            rows = (
                self._get_client()
                .table("positions_snapshot")
                .select(
                    "ticker,quantity,avg_cost,market_price,unrealized_pnl,currency,raw,snapshot_time_utc"
                )
                .in_("ticker", tickers)
                .order("snapshot_time_utc", desc=True)
                .execute()
                .data
                or []
            )
        except APIError:
            return {}
        latest: dict[str, dict[str, Any]] = {}
        for row in rows:
            ticker = str(row["ticker"]).upper()
            if ticker not in latest:
                latest[ticker] = row
        return latest

    def _get_position_tags(self, position_id: str) -> list[PositionTagItem]:
        rows = (
            self._get_client()
            .table("position_tags")
            .select("id,tag,source,created_at")
            .eq("position_id", position_id)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )
        return [
            PositionTagItem(
                id=row["id"],
                tag=row["tag"],
                source=row["source"],
                created_at_utc=datetime.fromisoformat(
                    row["created_at"].replace("Z", "+00:00")
                ),
            )
            for row in rows
        ]

    def _get_position_links(self, position_id: str) -> list[LinkedTriggerItem]:
        rows = (
            self._get_client()
            .table("trigger_position_links")
            .select("trigger_id,link_type,created_at")
            .eq("position_id", position_id)
            .order("created_at", desc=False)
            .execute()
            .data
            or []
        )
        return [
            LinkedTriggerItem(
                trigger_id=row["trigger_id"],
                link_type=row["link_type"],
                linked_at_utc=datetime.fromisoformat(
                    row["created_at"].replace("Z", "+00:00")
                ),
            )
            for row in rows
        ]

    def add_position_tag(
        self, *, position_id: str, tag: str, source: str
    ) -> PositionTagItem:
        payload = {"position_id": position_id, "tag": tag.strip(), "source": source}
        client = self._get_client()
        client.table("position_tags").insert(payload).execute()
        rows = (
            client.table("position_tags")
            .select("id,tag,source,created_at")
            .eq("position_id", position_id)
            .eq("tag", payload["tag"])
            .eq("source", source)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
            .data
            or []
        )
        if not rows:
            raise ValueError("Failed to create position tag")
        row = rows[0]
        return PositionTagItem(
            id=row["id"],
            tag=row["tag"],
            source=row["source"],
            created_at_utc=datetime.fromisoformat(
                row["created_at"].replace("Z", "+00:00")
            ),
        )

    def delete_position_tag(self, *, position_id: str, tag_id: str) -> None:
        client = self._get_client()
        existing = (
            client.table("position_tags")
            .select("id")
            .eq("position_id", position_id)
            .eq("id", tag_id)
            .limit(1)
            .execute()
            .data
            or []
        )
        if not existing:
            raise ValueError("Tag not found")
        client.table("position_tags").delete().eq("position_id", position_id).eq(
            "id", tag_id
        ).execute()

    def insert_position_snapshots(self, snapshot_rows: list[dict[str, Any]]) -> None:
        if not snapshot_rows:
            return
        self._get_client().table("positions_snapshot").insert(snapshot_rows).execute()

    def ensure_open_positions_for_tickers(self, tickers: list[str]) -> None:
        if not tickers:
            return
        client = self._get_client()
        existing_rows = (
            client.table("position_journal")
            .select("ticker")
            .eq("status", "open")
            .in_("ticker", tickers)
            .execute()
            .data
            or []
        )
        existing_tickers = {str(row["ticker"]).upper() for row in existing_rows}
        missing = [ticker for ticker in tickers if ticker.upper() not in existing_tickers]
        if not missing:
            return

        inserts = [
            {"ticker": ticker.upper(), "status": "open", "origin": "manual"}
            for ticker in missing
        ]
        client.table("position_journal").insert(inserts).execute()


supabase_service = SupabaseService()
