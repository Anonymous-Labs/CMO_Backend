from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[dict])
def get_posts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get all saved posts for the current user"""
    # For now, return empty list - implement when database models are ready
    return []


@router.post("/", response_model=dict)
def create_post(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    post_data: dict,
) -> Any:
    """Create a new saved post"""
    # For now, just return the data - implement when database models are ready
    return {
        "id": 1,
        "title": post_data.get("title", ""),
        "caption": post_data.get("caption", ""),
        "hashtags": post_data.get("hashtags", ""),
        "mode": post_data.get("mode", "image"),
        "status": "draft",
        "created_at": "2025-01-22T00:00:00Z",
        "user_id": current_user.id,
        "platforms": ["instagram"],
    }


@router.delete("/{post_id}")
def delete_post(
    *,
    db: Session = Depends(deps.get_db),
    post_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Delete a saved post"""
    # For now, just return success - implement when database models are ready
    return {"message": "Post deleted successfully"}
