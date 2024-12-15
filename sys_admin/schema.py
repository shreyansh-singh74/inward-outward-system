from pydantic import BaseModel


class UpdateUser(BaseModel):
    user_id: str
    role: str
    department: str
