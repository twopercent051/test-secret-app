from fastapi import APIRouter

from .secrets import router as secrets_router


router = APIRouter()
router.include_router(secrets_router)