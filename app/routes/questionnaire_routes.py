from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.questionnaire_service import QuestionnaireService
from app.schemas.questionnaire import QuestionnaireCreate, MonthlyReportUpdate
from app.database import get_db

router = APIRouter(prefix="/questionnaires", tags=["Questionnaires"])

def get_questionnaire_service(db: Session = Depends(get_db)):
    return QuestionnaireService(db)

@router.post("/", response_model=QuestionnaireCreate)
async def create_questionnaire(
    questionnaire: QuestionnaireCreate,
    service: QuestionnaireService = Depends(get_questionnaire_service)
):
    try:
        service.create_questionnaire(questionnaire)
        return questionnaire
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.patch("/{questionnaire_id}/monthly-report", response_model=dict)
async def update_monthly_report(
    questionnaire_id: int,
    update: MonthlyReportUpdate,
    service: QuestionnaireService = Depends(get_questionnaire_service),
    # Por ahora, user_id hardcodeado; en el futuro, obténlo del token JWT
    user_id: int = 1
):
    try:
        questionnaire = service.update_monthly_report(questionnaire_id, user_id, update)
        return questionnaire.monthly_report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el reporte mensual: {str(e)}")