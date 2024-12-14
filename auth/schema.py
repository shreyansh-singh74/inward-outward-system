from pydantic import BaseModel


class SignUpSchema(BaseModel):
    name: str
    role: str
    department: str
    email: str
    department: str
    tcet_email: str
    password: str


class LoginSchema(BaseModel):
    email: str
    password: str


class EmailSchema(BaseModel):
    email: str
