from fastapi import APIRouter

from .resources import location_contents

api_router = APIRouter(redirect_slashes=False)

api_router.include_router(
    location_contents.router,
    prefix="/async-msg",
    tags=["location", "contents", "async"],
)

__all__ = ["api_router"]
