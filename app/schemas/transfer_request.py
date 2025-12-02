from pydantic import BaseModel, Field

class TransferRequest(BaseModel):
    to_account: int = Field(gt=0, description="Recipient account ID")
    amount: float = Field(gt=0, description="Amount to transfer")