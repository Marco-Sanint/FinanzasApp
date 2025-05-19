# services/user_service.py
from app.services.verification_service import VerificationService
from sqlalchemy.orm import Session
from ..models.user import User, Role
from ..schemas.user import UserCreate, UserOut
from passlib.context import CryptContext
from fastapi import HTTPException
from ..utils.logging import logger

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.verification_service = VerificationService(db)

    def register_user(self, user: UserCreate):
        try:
            db_user = self.db.query(User).filter(User.email == user.email).first()
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            hashed_password = self.pwd_context.hash(user.password)
            new_user = User(
                email=user.email,
                password_hash=hashed_password,
                phone=user.phone,
                role=Role[user.role] if user.role in Role.__members__ else Role.client,
                is_verified=False
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)

            self.verification_service.create_verification_code(new_user.id, "email")
            return new_user
        except Exception as e:
            logger.error(f"Error in register_user: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")