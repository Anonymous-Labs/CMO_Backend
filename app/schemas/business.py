from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class BusinessBase(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    location: Optional[str] = None
    target_audience: Optional[str] = None
    brand_tone: Optional[str] = None
    primary_products: Optional[str] = None


class BusinessCreate(BusinessBase):
    name: str


class BusinessUpdate(BusinessBase):
    pass


class Business(BusinessBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class BusinessAsset(BaseModel):
    id: int
    business_id: int
    file_path: str
    original_filename: Optional[str] = None
    mime_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


