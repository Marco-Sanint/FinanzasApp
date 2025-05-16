from sqlalchemy import Column, Integer, Enum, DateTime, DECIMAL, ForeignKey, JSON
from sqlalchemy.sql import func
from .database import Base
import enum

class EmploymentStatus(enum.Enum):
    none = "none"
    part_time = "part_time"
    full_time = "full_time"

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employment_status = Column(Enum(EmploymentStatus), nullable=False)
    monthly_income = Column(DECIMAL(10, 2), nullable=False)
    estimated_expenses = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())