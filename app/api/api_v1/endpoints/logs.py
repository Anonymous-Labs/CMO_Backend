"""
Log endpoint for receiving frontend error logs
"""
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

from app import models, crud
from app.api import deps
from app.core.config import settings
from app.core.security import ALGORITHM
from app.core.logging_config import get_logger

logger = get_logger("logs")
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/access-token", auto_error=False)


class ErrorLogRequest(BaseModel):
    timestamp: str
    level: str
    message: str
    data: dict = {}
    userAgent: str = ""
    url: str = ""
    userId: str = ""


async def get_current_user_optional(
    db: Session = Depends(deps.get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[models.User]:
    """Optional dependency to get current user if authenticated"""
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        if sub is None:
            return None
        user_id = int(sub)
        user = crud.user.user.get(db, id=user_id)
        return user if user and crud.user.user.is_active(user) else None
    except Exception:
        return None


@router.post("/error")
async def log_error(
    *,
    log_entry: ErrorLogRequest,
    db: Session = Depends(deps.get_db),
    current_user: Optional[models.User] = Depends(get_current_user_optional),
) -> Any:
    """
    Receive error logs from frontend.
    """
    user_id = current_user.id if current_user else None
    
    logger.error(
        f"Frontend Error | User: {user_id} | {log_entry.message} | URL: {log_entry.url}",
        extra={
            "frontend_error": True,
            "user_id": user_id,
            "user_agent": log_entry.userAgent,
            "url": log_entry.url,
            "error_data": log_entry.data,
        }
    )
    
    return {"status": "logged"}

