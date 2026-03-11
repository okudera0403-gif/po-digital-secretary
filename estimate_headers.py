from core.database import Base
from sqlalchemy import Column, DateTime, Integer, String


class Estimate_headers(Base):
    __tablename__ = "estimate_headers"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    case_id = Column(Integer, nullable=True)
    category_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    product_code = Column(String, nullable=True)
    type_name = Column(String, nullable=True)
    side = Column(String, nullable=True)
    insurance_name = Column(String, nullable=True)
    base_price = Column(Integer, nullable=True)
    joint_total = Column(Integer, nullable=True)
    support_total = Column(Integer, nullable=True)
    foot_total = Column(Integer, nullable=True)
    addon_total = Column(Integer, nullable=True)
    parts_total = Column(Integer, nullable=True)
    grand_total = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)