# routes/verification_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models.verification_code import VerificationCode
from ..models.user import User
from ..schemas.verification import VerificationRequest, ResendVerificationRequest  # Añadir ResendVerificationRequest
from ..services.verification_service import VerificationService

router = APIRouter(prefix="/verification", tags=["Verification"])

@router.post("/verify")
async def verify_code(request: VerificationRequest, db: Session = Depends(get_db)):
    try:
        verification = db.query(VerificationCode).filter(
            VerificationCode.code == request.code,
            VerificationCode.type == "email"
        ).first()
        
        if not verification:
            raise HTTPException(status_code=404, detail="Código no encontrado")
        
        user = db.query(User).filter(User.id == verification.user_id, User.email == request.email).first()
        if not user:
            db.delete(verification)
            db.commit()
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if verification.expires_at < datetime.utcnow():
            db.delete(verification)
            db.commit()
            raise HTTPException(status_code=400, detail="Código expirado. Por favor, solicita un nuevo código de verificación.")
        
        user.is_verified = True
        db.delete(verification)
        db.commit()
        
        return {"message": "Usuario verificado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al verificar el código: {str(e)}")

@router.post("/resend-verification")
async def resend_verification(request: ResendVerificationRequest, db: Session = Depends(get_db)):
    try:
        # Buscar el usuario por email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el usuario no esté ya verificado
        if user.is_verified:
            raise HTTPException(status_code=400, detail="El usuario ya está verificado")
        
        # Verificar si hay un código de verificación activo (no expirado)
        existing_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == user.id,
            VerificationCode.type == "email",
            VerificationCode.expires_at >= datetime.utcnow()
        ).first()
        
        if existing_code:
            raise HTTPException(status_code=400, detail="Ya existe un código de verificación activo. Por favor, espera a que expire o verifica con el código actual.")
        
        # Generar un nuevo código de verificación
        verification_service = VerificationService(db)
        verification_service.create_verification_code(user.id, "email")
        
        return {"message": "Nuevo código de verificación generado exitosamente. Revisa tu correo (o los logs)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar un nuevo código: {str(e)}")