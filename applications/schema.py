from pydantic import BaseModel, Field
from typing import Optional


class CreateApplicationSchema(BaseModel):
    description: str = Field(..., max_length=256)
    role: str = Field(..., max_length=200)
    department: str = Field(..., max_length=200)


class UpdateApplicationSchema(BaseModel):
    status: str
    remark: Optional[str] = Field(None, max_length=200)
    referenceNumber: Optional[str] = Field(None, max_length=200)


class ForwardApplicationSchema(BaseModel):
    role: str = Field(..., max_length=200)
    department: str = Field(..., max_length=200)
    remark: Optional[str] = Field(None, max_length=200)
