from typing import Optional
from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    public_key: Optional[str] = None
