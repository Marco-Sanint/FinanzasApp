# routes/user_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.role import Role
from ..schemas.user import UserCreate, UserOut
from ..schemas.login import LoginRequest
from ..services.user_service import UserService
from ..utils.auth import verify_password, create_access_token

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/")
async def root():
    return {"message": "API funcionando"}

@router.post("/register", response_model=UserOut)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.register_user(user)

@router.post("/login")
async def login(request: LoginRequest, db: Session = Depends(get_db)):  # Cambiar a request: LoginRequest
    user = db.query(User).filter(User.email == request.email).first()  # Usar request.email
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Usuario no verificado")
    
    if not verify_password(request.password, user.password_hash):  # Usar request.password
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}