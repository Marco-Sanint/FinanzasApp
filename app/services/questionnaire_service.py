from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.questionnaire import QuestionnaireCreate, MonthlyReportUpdate, ExpenseEntry
from fastapi import HTTPException
from datetime import date

class QuestionnaireService:
    def __init__(self, db: Session):
        self.db = db

    def validate_questionnaire(self, questionnaire: QuestionnaireCreate) -> None:
        if "sources" not in questionnaire.ans1:
            raise ValueError("ans1 debe contener una clave 'sources' con una lista de fuentes de ingresos")
        if "exact_amount" not in questionnaire.ans2:
            raise ValueError("ans2 debe contener una clave 'exact_amount' con el ingreso mensual")
        if "gastos" not in questionnaire.ans3:
            raise ValueError("ans3 debe contener una clave 'gastos' con una lista de categorías de gastos")
        if not isinstance(questionnaire.ans3["gastos"], list):
            raise ValueError("La clave 'gastos' en ans3 debe ser una lista")
        if "answer" not in questionnaire.ans4:
            raise ValueError("ans4 debe contener una clave 'answer' con 'yes', 'no' o 'maybe'")

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
        # Buscar el cuestionario
        questionnaire = self.db.query(Questionnaire).filter(
            Questionnaire.id == questionnaire_id,
            Questionnaire.user_id == user_id
        ).first()

        if not questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no pertenece al usuario")

        # Inicializar monthly_report si es None
        if questionnaire.monthly_report is None:
            questionnaire.monthly_report = {"entries": [], "total": 0.0}

        # Agregar la fecha actual a la entrada de gasto
        expense_dict = update.expense.dict()
        expense_dict["date"] = date.today().isoformat()  # Fecha actual en formato ISO (e.g., "2025-05-18")

        # Agregar la nueva entrada de gasto
        questionnaire.monthly_report["entries"].append(expense_dict)

        # Actualizar el total
        questionnaire.monthly_report["total"] += update.expense.amount

        # Guardar los cambios
        self.db.commit()
        self.db.refresh(questionnaire)
        return questionnaire