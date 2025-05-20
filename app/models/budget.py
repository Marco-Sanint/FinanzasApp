from sqlalchemy import Column, Integer, JSON, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    period = Column(Date, nullable=False)
    recommended_budget = Column(JSON, nullable=True, default={})  # Ej: {"name": "50/30/20", "distribution": {"Necesidades": 500000, ...}}
    actual_expenses = Column(JSON, nullable=True, default=[])  # Lista de gastos reales
    report = Column(JSON, nullable=True, default={})  # Reporte generado
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)