from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps

router = APIRouter()


@router.get("/", response_model=List[dict])
def get_drafts(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get all drafts for the current user"""
    # For now, return empty list - implement when database models are ready
    return []


@router.post("/", response_model=dict)
def create_draft(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    draft_data: dict,
) -> Any:
    """Create a new draft"""
    # For now, just return the data - implement when database models are ready
    return {
        "id": 1,
        "title": draft_data.get("title", ""),
        "caption": draft_data.get("caption", ""),
        "hashtags": draft_data.get("hashtags", ""),
        "mode": draft_data.get("mode", "image"),
        "original_content_id": draft_data.get("original_content_id"),
        "created_at": "2025-01-22T00:00:00Z",
        "updated_at": "2025-01-22T00:00:00Z",
        "user_id": current_user.id,
    }


@router.put("/{draft_id}", response_model=dict)
def update_draft(
    *,
    db: Session = Depends(deps.get_db),
    draft_id: int,
    current_user: models.User = Depends(deps.get_current_user),
    draft_data: dict,
) -> Any:
    """Update a draft"""
    # For now, just return the updated data - implement when database models are ready
    return {
        "id": draft_id,
        "title": draft_data.get("title", ""),
        "caption": draft_data.get("caption", ""),
        "hashtags": draft_data.get("hashtags", ""),
        "mode": draft_data.get("mode", "image"),
        "original_content_id": draft_data.get("original_content_id"),
        "created_at": "2025-01-22T00:00:00Z",
        "updated_at": "2025-01-22T00:00:00Z",
        "user_id": current_user.id,
    }


@router.delete("/{draft_id}")
def delete_draft(
    *,
    db: Session = Depends(deps.get_db),
    draft_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Delete a draft"""
    # For now, just return success - implement when database models are ready
    return {"message": "Draft deleted successfully"}
