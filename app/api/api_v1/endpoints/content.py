from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.services.gemini import generate_social_content

router = APIRouter()


@router.post("/generate", response_model=schemas.ContentGenerateResponse)
def generate_content(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    req: schemas.ContentGenerateRequest,
) -> Any:
    # Get business profile
    business = crud.business.get_by_user_id(db, user_id=current_user.id)
    if not business:
        raise HTTPException(status_code=400, detail="Create business profile first")

    # Convert business to dict for the service
    business_info = {
        "name": business.name,
        "industry": business.industry,
        "description": business.description,
        "website": business.website,
        "location": business.location,
        "target_audience": business.target_audience,
        "brand_tone": business.brand_tone,
        "primary_products": business.primary_products,
    }

    # Get uploaded assets for the business
    assets = crud.business.get_assets_by_business_id(db, business_id=business.id)
    asset_list = []
    if assets:
        for asset in assets:
            asset_list.append({
                "id": asset.id,
                "file_path": asset.file_path,
                "original_filename": asset.original_filename,
                "mime_type": asset.mime_type,
            })

    # Generate content using Gemini AI (Nano Banana)
    result = generate_social_content(
        business_info=business_info,
        mode=req.mode,
        prompt=req.prompt,
        assets=asset_list
    )

    return result


@router.get("/", response_model=List[dict])
def get_content(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Get all generated content for the current user"""
    # For now, return empty list - implement when database models are ready
    return []


@router.delete("/{content_id}")
def delete_content(
    *,
    db: Session = Depends(deps.get_db),
    content_id: int,
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    """Delete generated content"""
    # For now, just return success - implement when database models are ready
    return {"message": "Content deleted successfully"}


