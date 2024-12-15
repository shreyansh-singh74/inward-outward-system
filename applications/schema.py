from pydantic import BaseModel


class CreateApplicationSchema(BaseModel):
    description: str
    role: str
    department: str


class UpdateApplicationSchema(BaseModel):
    status: str
