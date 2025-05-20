from sqlalchemy import Column, Integer, Enum, DateTime, Float, String, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum("income", "expense", name="transaction_type"), nullable=False)
    amount = Column(Float(10, 2), nullable=True)
    category = Column(Enum(
        "Arriendo", "Servicios", "Mercado", "Salud", "Seguros", "Comunicación", "Transporte",
        "Educación", "Antojos", "Domicilio", "Suscripciones", "Salidas", "Hobbies", "Ahorros",
        "Deudas", "Otros", name="transaction_category"
    ), nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)