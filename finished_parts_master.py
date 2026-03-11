from core.database import Base
from sqlalchemy import Column, Integer, String


class Finished_parts_master(Base):
    __tablename__ = "finished_parts_master"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    section = Column(String, nullable=False)
    subcategory = Column(String, nullable=True)
    name = Column(String, nullable=False)
    part_number = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    source_page = Column(Integer, nullable=True)
    manual_confirm = Column(String, nullable=True)
    estimate_use = Column(String, nullable=True)
    notes = Column(String, nullable=True)