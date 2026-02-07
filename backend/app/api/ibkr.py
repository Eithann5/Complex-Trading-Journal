from fastapi import APIRouter, HTTPException
from requests import RequestException

from app.schemas.positions import SnapshotRunResponse
from app.services.snapshot_service import snapshot_service

router = APIRouter(prefix="/ibkr", tags=["ibkr"])


@router.post("/snapshot/run", response_model=SnapshotRunResponse)
def run_ibkr_snapshot() -> SnapshotRunResponse:
    try:
        result = snapshot_service.run_snapshot()
        return SnapshotRunResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RequestException as exc:
        raise HTTPException(status_code=503, detail=f"IBKR gateway unavailable: {exc}") from exc
