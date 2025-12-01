from pydantic import BaseModel


class RepayLoanRequest(BaseModel):
    user_payment: float