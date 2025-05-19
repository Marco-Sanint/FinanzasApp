from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from ..database import get_db
from ..models.verification_code import VerificationCode
from ..models.user import User
from ..schemas.verification import VerificationRequest, ResendVerificationRequest, VerificationCodeOut
from ..services.verification_service import VerificationService
from ..utils.dependencies import get_current_user

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
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        if user.is_verified:
            raise HTTPException(status_code=400, detail="El usuario ya está verificado")
        
        existing_code = db.query(VerificationCode).filter(
            VerificationCode.user_id == user.id,
            VerificationCode.type == "email",
            VerificationCode.expires_at >= datetime.utcnow()
        ).first()
        
        if existing_code:
            raise HTTPException(status_code=400, detail="Ya existe un código de verificación activo. Por favor, espera a que expire o verifica con el código actual.")
        
        verification_service = VerificationService(db)
        verification_service.create_verification_code(user.id, "email")
        
        return {"message": "Nuevo código de verificación generado exitosamente. Revisa tu correo (o los logs)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al generar un nuevo código: {str(e)}")

@router.get("/{code_id}", response_model=VerificationCodeOut)
async def get_verification_code(
    code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    permissions = current_user.get_permissions()
    if not permissions.can_manage_verification_codes():
        raise HTTPException(status_code=403, detail="No tienes permiso para gestionar códigos de verificación")

    code = db.query(VerificationCode).filter(VerificationCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Código de verificación no encontrado")
    return code

@router.get("/", response_model=List[VerificationCodeOut])
async def get_all_verification_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    permissions = current_user.get_permissions()
    if not permissions.can_manage_verification_codes():
        raise HTTPException(status_code=403, detail="No tienes permiso para gestionar códigos de verificación")

    return db.query(VerificationCode).all()

@router.delete("/{code_id}")
async def delete_verification_code(
    code_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    permissions = current_user.get_permissions()
    if not permissions.can_manage_verification_codes():
        raise HTTPException(status_code=403, detail="No tienes permiso para gestionar códigos de verificación")

    code = db.query(VerificationCode).filter(VerificationCode.id == code_id).first()
    if not code:
        raise HTTPException(status_code=404, detail="Código de verificación no encontrado")

    db.delete(code)
    db.commit()
    return {"message": "Código de verificación eliminado exitosamente"}