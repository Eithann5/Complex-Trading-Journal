from fastapi import APIRouter

from app.api.alerts_feed import router as alerts_feed_router
from app.api.health import router as health_router
from app.api.positions import router as positions_router
from app.api.triggers import router as triggers_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(alerts_feed_router)
api_router.include_router(triggers_router)
api_router.include_router(positions_router)
