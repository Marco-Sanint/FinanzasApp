from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models.user import User
from ..models.role import Role
from ..schemas.user import UserCreate, UserOut
from ..schemas.login import LoginRequest
from ..services.user_service import UserService
from ..utils.auth import verify_password, create_access_token
from ..utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

@router.get("/", response_model=List[UserOut])
async def get_all_users(
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_user():
        raise HTTPException(status_code=403, detail="No tienes permiso para leer usuarios")

    return service.get_all_users()

@router.post("/register", response_model=UserOut)
async def register_user(
    user: UserCreate,
    service: UserService = Depends(get_user_service)
):
    try:
        return service.register_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Usuario no verificado")
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_read_user() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para leer este usuario")

    try:
        return service.get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    user_update: UserCreate,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_update_user() and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para actualizar este usuario")

    try:
        return service.update_user(user_id, user_update)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_delete_user():
        raise HTTPException(status_code=403, detail="No tienes permiso para eliminar usuarios")

    try:
        return service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.patch("/{user_id}/role", response_model=UserOut)
async def change_user_role(
    user_id: int,
    new_role: str,
    current_user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service)
):
    permissions = current_user.get_permissions()
    if not permissions.can_change_role():
        raise HTTPException(status_code=403, detail="No tienes permiso para cambiar roles")

    try:
        role = Role[new_role]
    except KeyError:
        raise HTTPException(status_code=400, detail=f"Rol inválido. Los roles válidos son: {', '.join([r.value for r in Role])}")

    try:
        return service.change_role(user_id, role)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))