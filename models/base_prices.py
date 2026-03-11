from core.database import Base
from sqlalchemy import Column, Integer, String


class Base_prices(Base):
    __tablename__ = "base_prices"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    code = Column(String, nullable=False)
    molding_price = Column(Integer, nullable=False)
    measurement_price = Column(Integer, nullable=False)
    remarks = Column(String, nullable=True)