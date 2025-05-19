# services/verification_service.py
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.verification_code import VerificationCode
import secrets
from ..utils.logging import logger

class VerificationService:
    def __init__(self, db: Session):
        self.db = db

    def create_verification_code(self, user_id: int, code_type: str) -> VerificationCode:
        code = secrets.token_hex(4)
        expires_at = datetime.utcnow() + timedelta(minutes=60)
        verification_code = VerificationCode(
            user_id=user_id,
            code=code,
            type=code_type,
            expires_at=expires_at
        )
        self.db.add(verification_code)
        self.db.commit()
        self.db.refresh(verification_code)
        logger.info(f"Verification code {code} sent to user {user_id}")
        return verification_code