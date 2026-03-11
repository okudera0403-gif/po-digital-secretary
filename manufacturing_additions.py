from core.database import Base
from sqlalchemy import Column, Integer, String


class Manufacturing_additions(Base):
    __tablename__ = "manufacturing_additions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    source_page = Column(Integer, nullable=True)