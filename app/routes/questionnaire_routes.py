from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.services.questionnaire_service import QuestionnaireService
from app.schemas.questionnaire import QuestionnaireCreate, MonthlyReportUpdate, QuestionnaireOut
from app.database import get_db
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/questionnaires", tags=["Questionnaires"])

def get_questionnaire_service(db: Session = Depends(get_db)):
    return QuestionnaireService(db)

@router.post("/", response_model=QuestionnaireCreate)
async def create_questionnaire(
    questionnaire: QuestionnaireCreate,
    current_user: User = Depends(get_current_user),
    service: QuestionnaireService = Depends(get_questionnaire_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_create_questionnaire():
        raise HTTPException(status_code=403, detail="No tienes permiso para crear cuestionarios")

    questionnaire.user_id = current_user.id
    try:
        service.create_questionnaire(questionnaire)
        return questionnaire
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@router.get("/{questionnaire_id}", response_model=QuestionnaireOut)
async def get_questionnaire(
    questionnaire_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.questionnaire import Questionnaire
    permissions = current_user.get_permissions()
    query = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id)
    if not permissions.can_read_questionnaire():
        query = query.filter(Questionnaire.user_id == current_user.id)

    questionnaire = query.first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no tienes permiso")
    return questionnaire

@router.get("/", response_model=List[QuestionnaireOut])
async def get_all_questionnaires(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.questionnaire import Questionnaire
    permissions = current_user.get_permissions()
    query = db.query(Questionnaire)
    if not permissions.can_read_questionnaire():
        query = query.filter(Questionnaire.user_id == current_user.id)

    return query.all()

@router.put("/{questionnaire_id}", response_model=QuestionnaireOut)
async def update_questionnaire(
    questionnaire_id: int,
    questionnaire_update: QuestionnaireCreate,
    current_user: User = Depends(get_current_user),
    service: QuestionnaireService = Depends(get_questionnaire_service),
    db: Session = Depends(get_db)
):
    from app.models.questionnaire import Questionnaire
    permissions = current_user.get_permissions()
    query = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id)
    if not permissions.can_update_questionnaire():
        query = query.filter(Questionnaire.user_id == current_user.id)

    questionnaire = query.first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no tienes permiso")

    questionnaire_update.user_id = current_user.id
    try:
        service.validate_questionnaire(questionnaire_update)
        questionnaire.user_id = questionnaire_update.user_id
        questionnaire.ans1 = questionnaire_update.ans1
        questionnaire.ans2 = questionnaire_update.ans2
        questionnaire.ans3 = questionnaire_update.ans3
        questionnaire.ans4 = questionnaire_update.ans4
        questionnaire.monthly_report = questionnaire_update.monthly_report
        db.commit()
        db.refresh(questionnaire)
        return questionnaire
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{questionnaire_id}")
async def delete_questionnaire(
    questionnaire_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.questionnaire import Questionnaire
    permissions = current_user.get_permissions()
    query = db.query(Questionnaire).filter(Questionnaire.id == questionnaire_id)
    if not permissions.can_delete_questionnaire():
        query = query.filter(Questionnaire.user_id == current_user.id)

    questionnaire = query.first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado o no tienes permiso")

    db.delete(questionnaire)
    db.commit()
    return {"message": "Cuestionario eliminado exitosamente"}

@router.patch("/{questionnaire_id}/monthly-report", response_model=dict)
async def update_monthly_report(
    questionnaire_id: int,
    update: MonthlyReportUpdate,
    current_user: User = Depends(get_current_user),
    service: QuestionnaireService = Depends(get_questionnaire_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_update_questionnaire():
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar cuestionarios")

    try:
        questionnaire = service.update_monthly_report(questionnaire_id, current_user.id, update)
        return questionnaire.monthly_report
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar el reporte mensual: {str(e)}")