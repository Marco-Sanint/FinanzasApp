from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from app.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class Role(PyEnum):
    client = "client"
    editor = "editor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    role = Column(Enum(Role), default=Role.client)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())