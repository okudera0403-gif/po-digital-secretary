from core.database import Base
from sqlalchemy import Column, Integer, String


class Orthotic_masters(Base):
    __tablename__ = "orthotic_masters"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    category = Column(String, nullable=False)
    name = Column(String, nullable=False)
    base_price_molding = Column(Integer, nullable=True)
    base_price_measurement = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=True)