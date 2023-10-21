from fastapi import APIRouter

from src.controllers import stats
from src.controllers import vacancy
from src.controllers import testing
from src.controllers import permission


def register_api_router(is_debug: bool) -> APIRouter:
    root_api_router = APIRouter(prefix="/api/v1" if is_debug else "")

    root_api_router.include_router(vacancy.router, prefix="/vacancy", tags=["Vacancy"])
    root_api_router.include_router(testing.router, prefix="/testing", tags=["Testing"])
    root_api_router.include_router(permission.router, prefix="/permission", tags=["Permission"])
    root_api_router.include_router(stats.router, prefix="", tags=["Stats"])

    return root_api_router
