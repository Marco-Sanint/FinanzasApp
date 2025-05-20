from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.budget import Budget
from app.models.questionnaire import Questionnaire
from app.schemas.budget import BudgetCreate
from .budget_recommendation import WeightedScoringRecommender
from datetime import datetime
from dateutil.relativedelta import relativedelta

class BudgetService:
    def __init__(self, db: Session):
        self.db = db
        self.recommender = WeightedScoringRecommender()

    def create_budget(self, budget: BudgetCreate, user_id: int):
        questionnaire = self.db.query(Questionnaire).filter(
            Questionnaire.id == budget.questionnaire_id,
            Questionnaire.user_id == user_id
        ).first()

        if not questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no pertenece al usuario")

        # Validar que monthly_report tenga datos
        if not questionnaire.monthly_report or not questionnaire.monthly_report.get("entries"):
            raise HTTPException(status_code=400, detail="El monthly_report debe contener gastos detallados para generar una recomendación")

        budget_name, distribution = self.recommender.recommend(questionnaire)

        db_budget = Budget(
            user_id=user_id,
            period=datetime.now().date().replace(day=1) + relativedelta(months=1),
            recommended_budget={"name": budget_name, "distribution": distribution},
            actual_expenses=[],
            report={}
        )

        self.db.add(db_budget)
        self.db.commit()
        self.db.refresh(db_budget)
        return db_budget

    def sync_budget(self, budget_id: int, user_id: int):
        from app.models.transaction import Transaction
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Budget.user_id == user_id
        ).first()

        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado o no pertenece al usuario")

        start_date = budget.period
        end_date = start_date + relativedelta(months=1)

        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date,
            Transaction.created_at < end_date,
            Transaction.type.lower() == "expense"
        ).all()

        budget.actual_expenses = []
        for transaction in transactions:
            expense_entry = {
                "category": transaction.category,
                "amount": float(transaction.amount),
                "description": transaction.description,
                "date": transaction.created_at.date().isoformat()
            }
            budget.actual_expenses.append(expense_entry)

        self.db.commit()
        self.db.refresh(budget)
        return budget

    def generate_budget_report(self, budget_id: int, user_id: int) -> dict:
        budget = self.db.query(Budget).filter(
            Budget.id == budget_id,
            Questionnaire.user_id == user_id
        ).first()

        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        today = datetime.now().date()
        if today < budget.period.replace(day=1) + relativedelta(months=1, days=-1):
            raise HTTPException(status_code=400, detail="El reporte solo se puede generar al final del mes")

        actual_expenses = {
            "entries": budget.actual_expenses,
            "total": sum(entry["amount"] for entry in budget.actual_expenses),
            "by_category": {}
        }

        for entry in budget.actual_expenses:
            category = entry["category"]
            amount = entry["amount"]
            actual_expenses["by_category"][category] = actual_expenses["by_category"].get(category, 0) + amount

        recommended_total = sum(budget.recommended_budget["distribution"].values())
        difference = recommended_total - actual_expenses["total"]
        status = "Dentro del presupuesto" if difference >= 0 else "Excedido"

        recommendations = []
        if difference >= 0:
            recommendations.append(f"¡Genial! Estuviste dentro del presupuesto y ahorraste ${difference:,.0f}. ¡Sigue así!")
        else:
            recommendations.append(f"Excediste el presupuesto por ${-difference:,.0f}. Revisa tus gastos en {', '.join(actual_expenses['by_category'].keys())}.")

        return {
            "period": budget.period.isoformat(),
            "recommended_budget": budget.recommended_budget,
            "actual_expenses": actual_expenses,
            "analysis": {
                "total_actual": actual_expenses["total"],
                "total_recommended": recommended_total,
                "difference": difference,
                "status": status
            },
            "recommendations": recommendations
        }