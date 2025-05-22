import os
from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserOut
from ..models.role import Role
from ..utils.auth import verify_password, get_password_hash
from ..services.verification_service import VerificationService
from ..utils.email_service import EmailService
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, db: Session, email_service: Optional[EmailService] = None):
        self.db = db
        self.email_service = email_service or EmailService(
            smtp_server=os.getenv("EMAIL_HOST"),
            smtp_port=int(os.getenv("EMAIL_PORT")),
            sender_email=os.getenv("EMAIL_USER"),
            sender_password=os.getenv("EMAIL_PASSWORD")
        )

    def register_user(self, user: UserCreate) -> User:
        # Verificar si el email ya existe
        existing_user = self.db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("El email ya está registrado")

        # Crear nuevo usuario con rol client por defecto
        db_user = User(
            email=user.email,
            phone=user.phone,
            password_hash=get_password_hash(user.password),
            role=Role.client if user.role not in Role.__members__ else Role[user.role]
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        logger.info(f"Usuario registrado con id: {db_user.id}, email: {db_user.email}")

        # Generar y enviar código de verificación
        verification_service = VerificationService(self.db)
        verification_code = verification_service.create_verification_code(db_user.id, "email")
        
        # Enviar correo con el código de verificación
        if not self.email_service.send_verification_code(db_user.email, verification_code.code):
            logger.error(f"Error al enviar el correo de verificación al usuario {db_user.email}")
            raise ValueError("No se pudo enviar el correo de verificación")
        
        logger.info(f"Código de verificación enviado al correo {db_user.email}")
        return db_user

    # Resto de los métodos permanecen igual
    def get_user(self, user_id: int) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise ValueError("Usuario no encontrado")
        return user

    def get_all_users(self) -> list[User]:
        return self.db.query(User).all()

    def update_user(self, user_id: int, user_update: UserCreate) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise ValueError("Usuario no encontrado")

        user.email = user_update.email
        user.phone = user_update.phone
        user.password_hash = get_password_hash(user_update.password)
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"User with id {user_id} updated successfully")
        return user

    def delete_user(self, user_id: int) -> dict:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise ValueError("Usuario no encontrado")

        self.db.delete(user)
        self.db.commit()
        logger.info(f"User with id {user_id} deleted successfully")
        return {"message": "Usuario eliminado exitosamente"}

    def change_role(self, user_id: int, new_role: Role) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User with id {user_id} not found")
            raise ValueError("Usuario no encontrado")

        user.role = new_role
        self.db.commit()
        self.db.refresh(user)
        logger.info(f"Role changed for user with id {user_id} to {new_role.value}")
        return user