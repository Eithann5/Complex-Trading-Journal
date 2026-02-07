from postgrest.exceptions import APIError
from fastapi import APIRouter, HTTPException

from app.schemas.positions import OkResponse, TriggerLinkRequest
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/triggers", tags=["triggers"])


@router.post("/{trigger_id}/link", response_model=OkResponse)
def link_trigger_to_position(trigger_id: str, payload: TriggerLinkRequest) -> OkResponse:
    try:
        supabase_service.link_trigger_to_position(
            trigger_id=trigger_id,
            position_id=payload.position_id,
            link_type=payload.link_type,
        )
        return OkResponse(ok=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
