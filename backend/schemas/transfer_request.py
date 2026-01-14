from pydantic import BaseModel, Field


class TransferRequest(BaseModel):
    recipient_username: str = Field(
        min_length=1,
        description="Username of the recipient: must match the destination account owner",
    )
    to_account: int = Field(gt=0, description="Recipient account ID")
    amount: float = Field(gt=0, description="Amount to transfer")
