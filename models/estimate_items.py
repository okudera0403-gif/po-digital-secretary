from core.database import Base
from sqlalchemy import Column, Integer, String


class Estimate_items(Base):
    __tablename__ = "estimate_items"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    estimate_id = Column(Integer, nullable=False)
    item_group = Column(String, nullable=True)
    item_name = Column(String, nullable=True)
    item_type = Column(String, nullable=True)
    unit_price = Column(Integer, nullable=True)
    quantity = Column(Integer, nullable=True)
    amount = Column(Integer, nullable=True)
    remarks = Column(String, nullable=True)