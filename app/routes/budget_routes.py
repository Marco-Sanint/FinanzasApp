from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetOut
from app.services.budget_service import BudgetService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])

def get_budget_service(db: Session = Depends(get_db)):
    return BudgetService(db)

@router.post("/", response_model=BudgetOut)
async def create_budget(
    budget: BudgetCreate,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_create_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para crear presupuestos")

    db_budget = service.create_budget(budget, current_user.id)
    return db_budget

@router.get("/{budget_id}", response_model=BudgetOut)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer presupuestos")

    return service.get_budget(budget_id, current_user.id)

@router.get("/", response_model=List[BudgetOut])
async def get_all_budgets(
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer presupuestos")

    return service.get_all_budgets(current_user.id)

@router.put("/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: int,
    budget_update: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_update_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar presupuestos")

    budget_dict = budget_update.dict(exclude_unset=True)
    return service.update_budget(budget_id, budget_dict, current_user.id)

@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    service: BudgetService = Depends(get_budget_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_delete_budget():
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar presupuestos")

    return service.delete_budget(budget_id, current_user.id)

@router.patch("/{budget_id}/sync")
def sync_budget(budget_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budget_service = BudgetService(db)
    return budget_service.sync_budget(budget_id, user.id)

@router.get("/{budget_id}/report")
def get_budget_report(budget_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    budget_service = BudgetService(db)
    return budget_service.generate_budget_report(budget_id, user.id)