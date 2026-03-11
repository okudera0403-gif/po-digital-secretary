from core.database import Base
from sqlalchemy import Column, Integer, String


class Repair_references(Base):
    __tablename__ = "repair_references"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    repair_category = Column(String, nullable=True)
    item_name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    remarks = Column(String, nullable=True)
    source = Column(String, nullable=True)