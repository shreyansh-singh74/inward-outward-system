from pydantic import BaseModel


class SignUpSchema(BaseModel):
    name: str
    department: str
    email: str


class LoginSchema(BaseModel):
    email: str
