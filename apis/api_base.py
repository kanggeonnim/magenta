<<<<<<< HEAD
from fastapi import APIRouter

from apis.routes import magenta

api_router = APIRouter()
api_router.include_router(magenta.router, prefix="/ai", tags=["ai"])
=======
from fastapi import APIRouter

from apis.routes import magenta

api_router = APIRouter()
api_router.include_router(magenta.router, prefix="/ai", tags=["ai"])
>>>>>>> 772e8b32625d8bc5d06fcb8c1232671816e3c1f2
