from pydantic import BaseModel
from typing import Optional, List

class ExpenseEntry(BaseModel):
    description: str  # Descripción del gasto (e.g., "Compra de supermercado")
    amount: float  # Monto del gasto (e.g., 150000.00)

class MonthlyReportUpdate(BaseModel):
    expense: ExpenseEntry  # Nueva entrada de gasto a agregar

class QuestionnaireCreate(BaseModel):
    user_id: int
    ans1: dict  # {"sources": ["Trabajo propio", "Apoyo de padres"]}
    ans2: dict  # {"exact_amount": 1700000.00}
    ans3: dict  # {"gastos": ["arriendo", "mercado", ...]}
    ans4: dict  # {"answer": "yes"}
    monthly_report: Optional[dict] = None  # {"entries": [...], "total": 5000.00}

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