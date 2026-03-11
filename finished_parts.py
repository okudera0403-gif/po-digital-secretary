from core.database import Base
from sqlalchemy import Column, Integer, String


class Finished_parts(Base):
    __tablename__ = "finished_parts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    part_group = Column(String, nullable=True)
    part_category = Column(String, nullable=True)
    part_type = Column(String, nullable=True)
    manufacturer = Column(String, nullable=True)
    model_no = Column(String, nullable=True)
    upper_price = Column(Integer, nullable=True)
    old_price = Column(Integer, nullable=True)
    unit_note = Column(String, nullable=True)
    remarks = Column(String, nullable=True)
    source = Column(String, nullable=True)