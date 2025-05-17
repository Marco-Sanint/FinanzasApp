from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
from app.database import Base
from sqlalchemy.sql import func

class VerificationCode(Base):
    __tablename__ = "verification_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    code = Column(String(255), nullable=False)
    type = Column(Enum("email", "sms", name="verification_type"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # 👈 CAMBIO CLAVE
