from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String


class Estimates(Base):
    __tablename__ = "estimates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    case_id = Column(Integer, nullable=True)
    category_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    molding_type = Column(String, nullable=True)
    sub_type = Column(String, nullable=True)
    price_mode = Column(String, nullable=True)
    base_price = Column(Float, nullable=True)
    surcharge_items = Column(String, nullable=True)
    total_price = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)