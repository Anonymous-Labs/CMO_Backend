import os
import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.models.business_asset import BusinessAsset

router = APIRouter()

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("/me", response_model=schemas.Business)
def get_my_business(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
) -> Any:
    business = crud.business.get_by_user_id(db, user_id=current_user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return business


@router.post("/me", response_model=schemas.Business)
def upsert_my_business(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    business_in: schemas.BusinessCreate,
) -> Any:
    existing = crud.business.get_by_user_id(db, user_id=current_user.id)
    if existing:
        updated = crud.business.update(db, db_obj=existing, obj_in=business_in)
        return updated
    created = crud.business.create_for_user(db, user_id=current_user.id, obj_in=business_in)
    return created


@router.put("/me", response_model=schemas.Business)
def update_my_business(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    business_in: schemas.BusinessUpdate,
) -> Any:
    existing = crud.business.get_by_user_id(db, user_id=current_user.id)
    if not existing:
        raise HTTPException(status_code=404, detail="Business profile not found")
    updated = crud.business.update(db, db_obj=existing, obj_in=business_in)
    return updated


@router.post("/me/assets", response_model=List[schemas.BusinessAsset])
def upload_business_assets(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user),
    files: List[UploadFile] = File(...),
) -> Any:
    business = crud.business.get_by_user_id(db, user_id=current_user.id)
    if not business:
        raise HTTPException(status_code=404, detail="Create business profile first")

    created_assets: List[BusinessAsset] = []
    for f in files:
        ext = os.path.splitext(f.filename or "")[1]
        safe_name = f"{uuid.uuid4().hex}{ext}"
        path = os.path.join(UPLOAD_DIR, safe_name)
        with open(path, "wb") as out:
            out.write(f.file.read())

        asset = BusinessAsset(
            business_id=business.id,
            file_path=path,
            original_filename=f.filename,
            mime_type=f.content_type,
        )
        db.add(asset)
        created_assets.append(asset)

    db.commit()
    for a in created_assets:
        db.refresh(a)
    return created_assets


