from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

# Definir la enumeración para las categorías
class CategoryEnum(str, Enum):
    ARRIENDO = "Arriendo"
    SERVICIOS = "Servicios"
    MERCADO = "Mercado"
    SALUD = "Salud"
    SEGUROS = "Seguros"
    COMUNICACION = "Comunicación"
    TRANSPORTE = "Transporte"
    EDUCACION = "Educación"
    ANTOJOS = "Antojos"
    DOMICILIO = "Domicilio"
    SUSCRIPCIONES = "Suscripciones"
    SALIDAS = "Salidas"
    HOBBIES = "Hobbies"
    AHORROS = "Ahorros"
    DEUDAS = "Deudas"
    OTROS = "Otros"

class TransactionBase(BaseModel):
    type: str  # Podrías usar un Enum para 'type' también (e.g., 'income', 'expense')
    amount: Optional[float] = None
    category: Optional[CategoryEnum] = None  # Usar la enumeración para validación
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionUpdate(TransactionBase):
    type: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[CategoryEnum] = None
    description: Optional[str] = None

class TransactionOut(TransactionBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }