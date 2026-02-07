from typing import Any

import requests

from app.config import settings


class IbkrService:
    def _require_config(self) -> tuple[str, str, bool]:
        if not settings.ibkr_base_url or not settings.ibkr_account_id:
            raise ValueError("IBKR_BASE_URL and IBKR_ACCOUNT_ID are required")
        return (
            settings.ibkr_base_url.rstrip("/"),
            settings.ibkr_account_id,
            settings.ibkr_verify_ssl,
        )

    def _get(self, path: str) -> Any:
        base_url, _account_id, verify_ssl = self._require_config()
        url = f"{base_url}{path}"
        response = requests.get(url, verify=verify_ssl, timeout=20)
        response.raise_for_status()
        return response.json()

    def fetch_open_positions(self) -> list[dict[str, Any]]:
        _base_url, account_id, _verify_ssl = self._require_config()
        page = 0
        rows: list[dict[str, Any]] = []

        while True:
            data = self._get(f"/v1/api/portfolio/{account_id}/positions/{page}")
            if not isinstance(data, list) or len(data) == 0:
                break
            rows.extend(data)
            page += 1

        return rows


ibkr_service = IbkrService()
