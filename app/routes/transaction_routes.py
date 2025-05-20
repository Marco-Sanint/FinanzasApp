from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut
from app.services.transaction_service import TransactionService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

def get_transaction_service(db: Session = Depends(get_db)):
    return TransactionService(db)

@router.post("/", response_model=TransactionOut)
async def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_create_transaction():
        raise HTTPException(status_code=403, detail="No tienes permiso para crear transacciones")

    transaction_dict = transaction.dict(exclude_unset=True)
    db_transaction = service.create_transaction(transaction_dict, current_user.id)
    return db_transaction

@router.get("/{transaction_id}", response_model=TransactionOut)
async def get_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_transaction():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer transacciones")

    return service.get_transaction(transaction_id, current_user.id)

@router.get("/", response_model=List[TransactionOut])
async def get_all_transactions(
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_transaction():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer transacciones")

    return service.get_all_transactions(current_user.id)

@router.put("/{transaction_id}", response_model=TransactionOut)
async def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_edit_transaction():
        raise HTTPException(status_code=403, detail="No tienes permiso para editar transacciones")

    transaction_dict = transaction_update.dict(exclude_unset=True)
    return service.update_transaction(transaction_id, transaction_dict, current_user.id)

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    service: TransactionService = Depends(get_transaction_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_delete_transaction():
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar transacciones")

    return service.delete_transaction(transaction_id, current_user.id)