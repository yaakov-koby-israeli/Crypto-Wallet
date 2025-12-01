from pydantic import BaseModel

class SetUpAccount(BaseModel):
    balance: float
    is_active: bool = True