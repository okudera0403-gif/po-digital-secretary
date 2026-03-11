from core.database import Base
from sqlalchemy import Column, Integer, String


class Product_part_rules(Base):
    __tablename__ = "product_part_rules"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    product_code = Column(String, nullable=False)
    product_name = Column(String, nullable=True)
    required_part_category = Column(String, nullable=False)
    necessity = Column(String, nullable=True)
    quantity_rule = Column(String, nullable=True)
    memo = Column(String, nullable=True)