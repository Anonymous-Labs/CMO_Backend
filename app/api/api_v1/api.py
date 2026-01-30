from fastapi import APIRouter

from app.api.api_v1.endpoints import auth, users, business, content, instagram, drafts, images, posts, chat, logs

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(business.router, prefix="/business", tags=["business"])
api_router.include_router(content.router, prefix="/content", tags=["content"])
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
api_router.include_router(drafts.router, prefix="/drafts", tags=["drafts"])
api_router.include_router(images.router, prefix="/images", tags=["images"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(logs.router, prefix="/logs", tags=["logs"])
