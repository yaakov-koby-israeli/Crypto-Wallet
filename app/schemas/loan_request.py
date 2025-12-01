from pydantic import BaseModel, Field
from enums import Payments, InterestRate

class LoanRequest(BaseModel):
    amount: float = Field(gt=0)
    duration_months: Payments
    interest_rate: InterestRate