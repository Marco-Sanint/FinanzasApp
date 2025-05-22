from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.budget import Budget
from app.models.questionnaire import Questionnaire
from app.schemas.budget import BudgetCreate
from .budget_recommendation import WeightedScoringRecommender
from datetime import datetime
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
import os

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

    def get_all_budgets(self, user_id: int) -> list[Budget]:
        """Obtiene todos los presupuestos de un usuario."""
        budgets = self.db.query(Budget).filter(Budget.user_id == user_id).all()
        return budgets

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
            Budget.user_id == user_id
        ).first()

        if not budget:
            raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

        today = datetime.now().date()
        if today < budget.period.replace(day=1) + relativedelta(months=1, days=-1):
            raise HTTPException(status_code=400, detail="El reporte solo se puede generar al final del mes")

        # Calcular gastos reales por categoría
        actual_expenses = {
            "entries": budget.actual_expenses,
            "total": sum(entry["amount"] for entry in budget.actual_expenses),
            "by_category": {}
        }
        for entry in budget.actual_expenses:
            category = entry["category"]
            amount = entry["amount"]
            actual_expenses["by_category"][category] = actual_expenses["by_category"].get(category, 0) + amount

        # Comparar con presupuesto recomendado
        recommended_budget = budget.recommended_budget["distribution"]
        recommended_total = sum(recommended_budget.values())
        difference = recommended_total - actual_expenses["total"]
        status = "Dentro del presupuesto" if difference >= 0 else "Excedido"

        # Análisis de desviaciones
        deviations = {}
        for category in set(recommended_budget.keys()).union(actual_expenses["by_category"].keys()):
            recommended = recommended_budget.get(category, 0)
            actual = actual_expenses["by_category"].get(category, 0)
            deviation = actual - recommended
            deviations[category] = {
                "recommended": recommended,
                "actual": actual,
                "deviation": deviation,
                "status": "Excedido" if deviation > 0 else "Dentro o por debajo"
            }

        # Recomendaciones detalladas
        recommendations = []
        if difference >= 0:
            recommendations.append(f"¡Excelente! Estuviste dentro del presupuesto y ahorraste ${difference:,.0f}. Considera destinar este excedente a ahorros o inversiones.")
            for category, data in deviations.items():
                if data["deviation"] < 0:
                    recommendations.append(f"- {category}: Gastaste ${-data['deviation']:,.0f} menos de lo recomendado. ¡Buen control!")
        else:
            recommendations.append(f"Excediste el presupuesto por ${-difference:,.0f}. Revisa tus gastos en las siguientes categorías:")
            for category, data in deviations.items():
                if data["deviation"] > 0:
                    recommendations.append(f"- {category}: Gastaste ${data['deviation']:,.0f} más de lo recomendado. Considera reducir gastos en esta área.")

        # Generar gráficos
        output_dir = "reports"
        os.makedirs(output_dir, exist_ok=True)
        budget_id_str = str(budget_id)

        # Gráfico de barras
        categories = list(set(recommended_budget.keys()).union(actual_expenses["by_category"].keys()))
        recommended_values = [recommended_budget.get(cat, 0) for cat in categories]
        actual_values = [actual_expenses["by_category"].get(cat, 0) for cat in categories]

        plt.figure(figsize=(10, 6))
        bar_width = 0.35
        x = range(len(categories))
        plt.bar([i - bar_width/2 for i in x], recommended_values, bar_width, label="Recomendado", color="skyblue")
        plt.bar([i + bar_width/2 for i in x], actual_values, bar_width, label="Real", color="salmon")
        plt.xlabel("Categorías")
        plt.ylabel("Monto (COP)")
        plt.title("Comparación de Presupuesto Recomendado vs. Real")
        plt.xticks(x, categories, rotation=45)
        plt.legend()
        plt.tight_layout()
        bar_chart_path = f"{output_dir}/bar_chart_{budget_id_str}.png"
        plt.savefig(bar_chart_path)
        plt.close()

        # Gráfico circular
        pie_chart_path = None
        if actual_expenses["by_category"]:
            plt.figure(figsize=(8, 8))
            plt.pie(
                list(actual_expenses["by_category"].values()),
                labels=list(actual_expenses["by_category"].keys()),
                autopct="%1.1f%%",
                startangle=140,
                colors=['#ff9999','#66b3ff','#99ff99','#ffcc99']
            )
            plt.title("Distribución de Gastos Reales")
            pie_chart_path = f"{output_dir}/pie_chart_{budget_id_str}.png"
            plt.savefig(pie_chart_path)
            plt.close()

        # Guardar reporte en la base de datos
        report = {
            "period": budget.period.isoformat(),
            "recommended_budget": budget.recommended_budget,
            "actual_expenses": actual_expenses,
            "analysis": {
                "total_actual": actual_expenses["total"],
                "total_recommended": recommended_total,
                "difference": difference,
                "status": status,
                "deviations": deviations
            },
            "recommendations": recommendations,
            "charts": {
                "bar_chart": bar_chart_path,
                "pie_chart": pie_chart_path
            }
        }
        budget.report = report
        self.db.commit()
        self.db.refresh(budget)

        return report