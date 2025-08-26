from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str



class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: Optional[str] = None


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str