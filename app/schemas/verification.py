# schemas/verification.py
from pydantic import BaseModel

class VerificationRequest(BaseModel):
    email: str
    code: str

class ResendVerificationRequest(BaseModel):
    email: str