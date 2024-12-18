from pydantic import BaseModel
from typing import Optional


class CreateApplicationSchema(BaseModel):
    description: str
    role: str
    department: str


class UpdateApplicationSchema(BaseModel):
    status: str
    remark: Optional[str]
    referenceNumber: Optional[str]


class ForwardApplicationSchema(BaseModel):
    role: str
    department: str
    remark: Optional[str]
