from core.database import Base
from sqlalchemy import Column, Integer, String


class Manufacturing_elements(Base):
    __tablename__ = "manufacturing_elements"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    category = Column(String, nullable=True)
    element_group = Column(String, nullable=True)
    name = Column(String, nullable=True)
    spec = Column(String, nullable=True)
    price = Column(Integer, nullable=True)
    remarks = Column(String, nullable=True)
    source = Column(String, nullable=True)