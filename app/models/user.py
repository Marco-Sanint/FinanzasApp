from sqlalchemy import Column, Integer, String, Enum, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base
import enum

class Role(enum.Enum):
    client = "client"
    editor = "editor"
    admin = "admin"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    is_verified = Column(Boolean, default=False)
    role = Column(Enum(Role), nullable=False, default=Role.client)
    created_at = Column(DateTime, server_default=func.now())