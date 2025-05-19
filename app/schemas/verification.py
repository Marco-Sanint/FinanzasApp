from pydantic import BaseModel
from datetime import datetime

class VerificationRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str

class VerificationCodeOut(BaseModel):
    id: int
    user_id: int
    code: str
    type: str
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }