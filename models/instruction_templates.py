from core.database import Base
from sqlalchemy import Column, Integer, String


class Instruction_templates(Base):
    __tablename__ = "instruction_templates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    product_code = Column(String, nullable=False)
    product_name = Column(String, nullable=True)
    field_name = Column(String, nullable=False)
    input_type = Column(String, nullable=False)
    required_flag = Column(Integer, nullable=True)
    option_values = Column(String, nullable=True)
    sort_order = Column(Integer, nullable=False)