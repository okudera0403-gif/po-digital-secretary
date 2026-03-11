from core.database import Base
from sqlalchemy import Column, Float, Integer, String


class Product_price_rules(Base):
    __tablename__ = "product_price_rules"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    category_name = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    molding_type = Column(String, nullable=True)
    sub_type = Column(String, nullable=True)
    price_input_mode = Column(String, nullable=True)
    base_price_molding = Column(Float, nullable=True)
    base_price_measurement = Column(Float, nullable=True)
    surcharge_label = Column(String, nullable=True)
    surcharge_price = Column(Float, nullable=True)
    remarks = Column(String, nullable=True)
    source = Column(String, nullable=True)