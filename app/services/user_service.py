from sqlalchemy.orm import Session
from ..models.user import User, Role
from ..schemas.user import UserCreate, UserOut
from passlib.context import CryptContext
import secrets
from datetime import datetime, timedelta
from ..models.verification_code import VerificationCode
from fastapi import HTTPException

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

            # Generar código de verificación
            verification_code = secrets.token_hex(4)
            expires_at = datetime.utcnow() + timedelta(minutes=15)
            new_code = VerificationCode(
                user_id=new_user.id,
                code=verification_code,
                type="email",
                expires_at=expires_at
                # No especificamos created_at, el servidor lo maneja
            )
            self.db.add(new_code)
            self.db.commit()

            print(f"Verification code {verification_code} sent to {user.email}")
            return new_user
        except Exception as e:
            print(f"Error in register_user: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")