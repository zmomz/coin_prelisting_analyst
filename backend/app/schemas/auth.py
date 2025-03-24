from pydantic import EmailStr

from app.schemas import SchemaBase


class Token(SchemaBase):
    access_token: str
    token_type: str


class LoginRequest(SchemaBase):
    email: EmailStr
    password: str
