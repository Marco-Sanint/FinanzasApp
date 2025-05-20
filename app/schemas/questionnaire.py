from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .transaction import CategoryEnum

class ExpenseEntry(BaseModel):
    category: CategoryEnum
    amount: float
    description: Optional[str] = None
    date: Optional[str] = None

class MonthlyReportUpdate(BaseModel):
    expense: ExpenseEntry

class QuestionnaireCreate(BaseModel):
    user_id: int
    ans1: dict  # Ej: {"sources": ["Trabajo propio"]}
    ans2: dict  # Ej: {"exact_amount": 1700000.00}
    ans3: dict  # Ej: {"gastos": ["Mercado", "Servicios", "Arriendo"]}
    ans4: dict  # Ej: {"answer": "yes", "savings_interest": "maybe"}
    monthly_report: Optional[dict] = None

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "ans1": {"sources": ["Trabajo propio", "Apoyo de padres o familiares"]},
                "ans2": {"exact_amount": 1700000.00},
                "ans3": {"gastos": ["Mercado", "Servicios", "Arriendo"]},
                "ans4": {"answer": "yes", "savings_interest": "maybe"},
                "monthly_report": None
            }
        }

class QuestionnaireOut(BaseModel):
    id: int
    user_id: int
    ans1: dict
    ans2: dict
    ans3: dict
    ans4: dict
    monthly_report: Optional[dict]
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }