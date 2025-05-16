from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from .database import Base

class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(Date, nullable=False)
    recommended_budget = Column(JSON)
    actual_expenses = Column(JSON)
    report = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())