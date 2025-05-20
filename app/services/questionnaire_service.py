from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.questionnaire import QuestionnaireCreate, MonthlyReportUpdate, ExpenseEntry
from app.models.transaction import Transaction
from fastapi import HTTPException
from datetime import date
from app.schemas.transaction import CategoryEnum
from sqlalchemy.orm.attributes import flag_modified

class QuestionnaireService:
    def __init__(self, db: Session):
        self.db = db

    def validate_questionnaire(self, questionnaire: QuestionnaireCreate) -> None:
        if "sources" not in questionnaire.ans1:
            raise ValueError("ans1 debe contener una clave 'sources' con una lista de fuentes de ingresos")
        if "exact_amount" not in questionnaire.ans2:
            raise ValueError("ans2 debe contener una clave 'exact_amount' con el ingreso mensual")
        if "gastos" not in questionnaire.ans3 or not isinstance(questionnaire.ans3["gastos"], list):
            raise ValueError("ans3 debe contener una clave 'gastos' con una lista de categorías")
        if "answer" not in questionnaire.ans4:
            raise ValueError("ans4 debe contener una clave 'answer' con 'yes', 'no' o 'maybe'")
        
        # Validar categorías en gastos
        valid_categories = [cat.value for cat in CategoryEnum]
        for category in questionnaire.ans3["gastos"]:
            if category not in valid_categories:
                raise ValueError(f"Categoría inválida: {category}. Debe ser una de {valid_categories}")

        # Validar monthly_report si está presente
        if questionnaire.monthly_report:
            if not isinstance(questionnaire.monthly_report, dict) or "entries" not in questionnaire.monthly_report or "total" not in questionnaire.monthly_report:
                raise ValueError("monthly_report debe ser un diccionario con claves 'entries' y 'total'")
            if not isinstance(questionnaire.monthly_report["entries"], list):
                raise ValueError("monthly_report.entries debe ser una lista")
            if not isinstance(questionnaire.monthly_report["total"], (int, float)):
                raise ValueError("monthly_report.total debe ser un número")
            for entry in questionnaire.monthly_report["entries"]:
                if not isinstance(entry, dict) or "category" not in entry or "amount" not in entry:
                    raise ValueError("Cada entrada en monthly_report.entries debe tener 'category' y 'amount'")
                if entry["category"] not in valid_categories:
                    raise ValueError(f"Categoría inválida en monthly_report: {entry['category']}")

    def create_questionnaire(self, questionnaire: QuestionnaireCreate):
        from app.models.questionnaire import Questionnaire
        self.validate_questionnaire(questionnaire)
        db_questionnaire = Questionnaire(
            user_id=questionnaire.user_id,
            ans1=questionnaire.ans1,
            ans2=questionnaire.ans2,
            ans3=questionnaire.ans3,
            ans4=questionnaire.ans4,
            monthly_report=questionnaire.monthly_report
        )
        self.db.add(db_questionnaire)
        self.db.commit()
        self.db.refresh(db_questionnaire)
        return db_questionnaire

    def update_monthly_report(self, questionnaire_id: int, user_id: int, update: MonthlyReportUpdate):
        from app.models.questionnaire import Questionnaire
        questionnaire = self.db.query(Questionnaire).filter(
            Questionnaire.id == questionnaire_id,
            Questionnaire.user_id == user_id
        ).first()

        if not questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no pertenece al usuario")

        # Inicializar monthly_report si es None
        if questionnaire.monthly_report is None:
            questionnaire.monthly_report = {"entries": [], "total": 0.0}

        # Asegurarse de que entries es una lista
        if not isinstance(questionnaire.monthly_report.get("entries"), list):
            questionnaire.monthly_report["entries"] = []

        # Añadir el nuevo gasto
        expense_dict = update.expense.dict()
        expense_dict["date"] = date.today().isoformat()
        questionnaire.monthly_report["entries"].append(expense_dict)
        questionnaire.monthly_report["total"] = questionnaire.monthly_report.get("total", 0.0) + update.expense.amount

        # Marcar el campo monthly_report como modificado
        flag_modified(questionnaire, "monthly_report")

        self.db.commit()
        self.db.refresh(questionnaire)
        return questionnaire

    def sync_questionnaire_with_transactions(self, questionnaire_id: int, user_id: int, start_date: date, end_date: date):
        from app.models.questionnaire import Questionnaire
        questionnaire = self.db.query(Questionnaire).filter(
            Questionnaire.id == questionnaire_id,
            Questionnaire.user_id == user_id
        ).first()

        if not questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no pertenece al usuario")

        transactions = self.db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.created_at >= start_date,
            Transaction.created_at < end_date,
            Transaction.type.lower() == "expense"
        ).all()

        questionnaire.monthly_report = {"entries": [], "total": 0.0}
        for transaction in transactions:
            expense_entry = {
                "category": transaction.category,
                "amount": float(transaction.amount),
                "description": transaction.description,
                "date": transaction.created_at.date().isoformat()
            }
            questionnaire.monthly_report["entries"].append(expense_entry)
            questionnaire.monthly_report["total"] += float(transaction.amount)

        # Marcar el campo monthly_report como modificado
        flag_modified(questionnaire, "monthly_report")

        self.db.commit()
        self.db.refresh(questionnaire)
        return questionnaire