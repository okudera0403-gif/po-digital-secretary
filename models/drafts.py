from core.database import Base
from sqlalchemy import Column, DateTime, Integer, String


class Drafts(Base):
    __tablename__ = "drafts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    draft_data = Column(String, nullable=True)
    case_number = Column(String, nullable=True)
    draft_status = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)