from pydantic import BaseModel
from typing import Optional
from datetime import datetime  # <- FALTA ESTO

class UserBase(BaseModel):
    email: str
    phone: Optional[str] = None
    role: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
