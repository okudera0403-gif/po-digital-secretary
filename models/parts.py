from core.database import Base
from sqlalchemy import Boolean, Column, Float, Integer, String


class Parts(Base):
    __tablename__ = "parts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    part_type = Column(String, nullable=True)
    maker = Column(String, nullable=True)
    ministry_registered = Column(Boolean, nullable=True)