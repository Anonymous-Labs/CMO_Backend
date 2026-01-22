from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, business, content

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
