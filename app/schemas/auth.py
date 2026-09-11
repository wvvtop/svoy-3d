from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Схема для логина"""
    email: EmailStr
    password: str

class RegisterRequest(BaseModel):
    """Схема для регистрации"""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Схема для получения токена"""
    access_token: str
    token_type: str = "bearer"
