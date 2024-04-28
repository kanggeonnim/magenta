from fastapi import APIRouter

from apis.routes import magenta

api_router = APIRouter()
api_router.include_router(magenta.router, prefix="/ai", tags=["ai"])