from typing import Optional, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.business import Business
from app.models.business_asset import BusinessAsset
from app.schemas.business import BusinessCreate, BusinessUpdate


class CRUDBusiness(CRUDBase[Business, BusinessCreate, BusinessUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[Business]:
        return db.query(Business).filter(Business.user_id == user_id).first()

    def create_for_user(self, db: Session, *, user_id: int, obj_in: BusinessCreate) -> Business:
        db_obj = Business(user_id=user_id, **obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_assets_by_business_id(self, db: Session, *, business_id: int) -> List[BusinessAsset]:
        return db.query(BusinessAsset).filter(BusinessAsset.business_id == business_id).all()


business = CRUDBusiness(Business)


