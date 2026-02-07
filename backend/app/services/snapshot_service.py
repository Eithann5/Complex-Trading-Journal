from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.services.ibkr_service import ibkr_service
from app.services.supabase_service import supabase_service


class SnapshotService:
    def _to_decimal(self, value: Any, default: str = "0") -> Decimal:
        if value is None:
            return Decimal(default)
        try:
            return Decimal(str(value))
        except Exception:  # noqa: BLE001
            return Decimal(default)

    def _map_ibkr_position(self, row: dict[str, Any], snapshot_time_utc: str) -> dict[str, Any]:
        ticker = str(row.get("contractDesc") or row.get("ticker") or "").upper().strip()
        quantity = self._to_decimal(row.get("position"))
        avg_cost = self._to_decimal(row.get("avgCost"), default=str(row.get("avgPrice") or "0"))
        market_price = self._to_decimal(row.get("mktPrice")) if row.get("mktPrice") is not None else None
        unrealized_pnl = (
            self._to_decimal(row.get("unrealizedPnl")) if row.get("unrealizedPnl") is not None else None
        )
        currency = row.get("currency")

        return {
            "snapshot_time_utc": snapshot_time_utc,
            "ticker": ticker,
            "quantity": float(quantity),
            "avg_cost": float(avg_cost),
            "market_price": float(market_price) if market_price is not None else None,
            "unrealized_pnl": float(unrealized_pnl) if unrealized_pnl is not None else None,
            "currency": currency,
            "raw": row,
        }

    def run_snapshot(self) -> dict[str, Any]:
        ibkr_rows = ibkr_service.fetch_open_positions()
        snapshot_time_utc = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        snapshot_rows = [
            self._map_ibkr_position(row, snapshot_time_utc)
            for row in ibkr_rows
            if str(row.get("contractDesc") or row.get("ticker") or "").strip()
        ]

        if snapshot_rows:
            supabase_service.insert_position_snapshots(snapshot_rows)
            tickers = sorted({row["ticker"] for row in snapshot_rows})
            supabase_service.ensure_open_positions_for_tickers(tickers)
        else:
            tickers = []

        return {
            "ok": True,
            "snapshots_created": len(snapshot_rows),
            "tickers": tickers,
            "snapshot_time_utc": snapshot_time_utc,
        }


snapshot_service = SnapshotService()
