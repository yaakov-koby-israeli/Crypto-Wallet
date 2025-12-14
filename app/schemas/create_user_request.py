from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str = Field(min_length=6, description="Password must be at least 6 characters long")
    role: str
    public_key: Optional[str] = None

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if not value or len(value.strip()) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value
