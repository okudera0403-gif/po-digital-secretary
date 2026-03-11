from core.database import Base
from sqlalchemy import Column, Integer, String


class Option_masters(Base):
    __tablename__ = "option_masters"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    group_name = Column(String, nullable=False)
    item_name = Column(String, nullable=False)
    price = Column(Integer, nullable=True)
    sort_order = Column(Integer, nullable=True)