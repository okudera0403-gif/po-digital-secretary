from core.database import Base
from sqlalchemy import Column, Integer, String


class Insurance_types(Base):
    __tablename__ = "insurance_types"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    name_en = Column(String, nullable=True)
    sort_order = Column(Integer, nullable=True)