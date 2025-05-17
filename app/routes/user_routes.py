from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User, Role  # Añadir Role al import
from ..schemas.user import UserCreate, UserOut
from ..services.user_service import UserService
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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