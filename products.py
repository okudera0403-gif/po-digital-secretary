from core.database import Base
from sqlalchemy import Column, Float, Integer, String


class Products(Base):
    __tablename__ = "products"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    category_id = Column(Integer, nullable=True)
    name = Column(String, nullable=False)
    product_code = Column(String, nullable=True)
    type_variant = Column(String, nullable=True)
    structure_notes = Column(String, nullable=True)
    durability_years = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    base_price = Column(Float, nullable=True)
    source = Column(String, nullable=True)