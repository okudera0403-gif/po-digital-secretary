from core.database import Base
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String


class Case_opinions(Base):
    __tablename__ = "case_opinions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    case_id = Column(Integer, nullable=False)
    opinion_type_purchase = Column(Boolean, nullable=True)
    opinion_type_repair = Column(Boolean, nullable=True)
    opinion_type_loan = Column(Boolean, nullable=True)
    opinion_type_special = Column(Boolean, nullable=True)
    disease_name = Column(String, nullable=True)
    disability_name_part = Column(String, nullable=True)
    disability_condition = Column(String, nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    usage_place_home = Column(Boolean, nullable=True)
    usage_place_work = Column(Boolean, nullable=True)
    usage_place_facility = Column(Boolean, nullable=True)
    usage_place_school = Column(Boolean, nullable=True)
    usage_place_other = Column(Boolean, nullable=True)
    usage_place_other_text = Column(String, nullable=True)
    frequency_per_day = Column(String, nullable=True)
    frequency_per_week = Column(String, nullable=True)
    orthosis_name = Column(String, nullable=True)
    expected_effect = Column(String, nullable=True)
    parts_text = Column(String, nullable=True)
    reason_daily_life_checked = Column(Boolean, nullable=True)
    reason_daily_life = Column(String, nullable=True)
    reason_work_school_checked = Column(Boolean, nullable=True)
    reason_work_school = Column(String, nullable=True)
    reason_other_checked = Column(Boolean, nullable=True)
    reason_other = Column(String, nullable=True)
    doctor_name = Column(String, nullable=True)
    department_name = Column(String, nullable=True)
    medical_institution = Column(String, nullable=True)
    opinion_date = Column(String, nullable=True)
    generated_draft = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), nullable=True)