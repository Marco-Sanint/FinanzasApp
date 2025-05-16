from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import SessionLocal, get_db
from .models.user import User, Role
from .schemas.user import UserCreate, UserOut
from passlib.context import CryptContext

app = FastAPI(title="Gestor de Finanzas Personales")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.get("/")
async def root():
    return {"message": "API funcionando"}

@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,
        role=Role[user.role] if user.role in Role.__members__ else Role.client,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user