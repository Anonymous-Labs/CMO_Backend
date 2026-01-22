from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class Business(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False, index=True)

    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    website = Column(String, nullable=True)
    location = Column(String, nullable=True)

    # comma-separated or simple text fields for now (keep it lightweight)
    target_audience = Column(String, nullable=True)
    brand_tone = Column(String, nullable=True)
    primary_products = Column(Text, nullable=True)

    user = relationship("User")


