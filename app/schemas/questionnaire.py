from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ExpenseEntry(BaseModel):
    description: str
    amount: float

class MonthlyReportUpdate(BaseModel):
    expense: ExpenseEntry

class QuestionnaireCreate(BaseModel):
    user_id: int
    ans1: dict
    ans2: dict
    ans3: dict
    ans4: dict
    monthly_report: Optional[dict] = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "ans1": {"sources": ["Trabajo propio", "Apoyo de padres o familiares"]},
                "ans2": {"exact_amount": 1700000.00},
                "ans3": {"gastos": ["arriendo", "servicios", "mercado"]},
                "ans4": {"answer": "yes"},
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