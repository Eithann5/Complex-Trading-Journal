from postgrest.exceptions import APIError
from fastapi import APIRouter, HTTPException

from app.schemas.positions import (
    OkResponse,
    OpenPositionItem,
    PositionPatchRequest,
    PositionTagCreateRequest,
    PositionTagItem,
)
from app.services.supabase_service import supabase_service

router = APIRouter(prefix="/positions", tags=["positions"])


@router.get("/open", response_model=list[OpenPositionItem])
def get_open_positions() -> list[OpenPositionItem]:
    try:
        return supabase_service.list_open_positions()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.patch("/{position_id}", response_model=OpenPositionItem)
def patch_position(position_id: str, payload: PositionPatchRequest) -> OpenPositionItem:
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="At least one field is required")
    try:
        return supabase_service.update_position(position_id, updates)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/{position_id}/tags", response_model=PositionTagItem)
def add_position_tag(position_id: str, payload: PositionTagCreateRequest) -> PositionTagItem:
    try:
        return supabase_service.add_position_tag(
            position_id=position_id,
            tag=payload.tag,
            source=payload.source,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{position_id}/tags/{tag_id}", response_model=OkResponse)
def delete_position_tag(position_id: str, tag_id: str) -> OkResponse:
    try:
        supabase_service.delete_position_tag(position_id=position_id, tag_id=tag_id)
        return OkResponse(ok=True)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except APIError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
