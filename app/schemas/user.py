from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    phone: str | None = None
    role: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True