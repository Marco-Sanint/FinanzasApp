from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional, List
from .transaction import CategoryEnum

class ExpenseEntry(BaseModel):
    category: CategoryEnum
    amount: float
    description: Optional[str] = None
    date: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "category": "Mercado",
                "amount": 300000.00,
                "description": "Compra de alimentos",
                "date": "2025-05-20"
            }
        }

class BudgetBase(BaseModel):
    period: date
    recommended_budget: Optional[dict] = None
    actual_expenses: Optional[List[dict]] = None
    report: Optional[dict] = None

class BudgetCreate(BaseModel):
    questionnaire_id: int

class BudgetUpdate(BaseModel):
    period: Optional[date] = None
    recommended_budget: Optional[dict] = None
    actual_expenses: Optional[List[dict]] = None
    report: Optional[dict] = None

class BudgetOut(BaseModel):
    id: int
    user_id: int
    period: date
    recommended_budget: Optional[dict] = None
    actual_expenses: Optional[List[dict]] = None
    report: Optional[dict] = None
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }