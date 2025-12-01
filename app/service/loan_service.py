from sqlalchemy.orm import Session
from enums import BidStatus
from models import Users, Loans, Account
from app.schemas.loan_request import LoanRequest
from datetime import datetime, timedelta

def request_loan_for_account(db: Session, user: Users, loan_request_data: LoanRequest,) -> Loans:

    """
    Creates a loan record and updates user account.
    Handles loan rules.
    """

    # Ensure and fetch the user has an account
    account = db.query(Account).filter(Account.user_id == user.id).first()
    if not account:
        raise ValueError("User must have an account before requesting a loan.")

    if account.active_loan:
        raise ValueError("You already have an active loan")

    if loan_request_data.amount > account.balance:
        raise ValueError("Requested loan amount exceeds account balance")

    # Prepare loan duration
    months = loan_request_data.duration_months.value

    # Calculate interest
    interest_amount = loan_request_data.amount * loan_request_data.interest_rate.value
    total_payable = loan_request_data.amount + interest_amount

    # Loan request time (satisfies NOT NULL on start_date)
    request_time = datetime.utcnow()

    # Provisional end date (will be updated on approval)
    provisional_end = request_time + timedelta(days=30 * months)

    # Create loan (row)
    new_loan = Loans(
        account_id=account.account_id,
        amount = loan_request_data.amount,
        interest_rate=loan_request_data.interest_rate,
        duration_months = loan_request_data.duration_months,
        start_date = request_time.strftime("%Y-%m-%d %H:%M:%S"),
        end_date=provisional_end.strftime("%Y-%m-%d %H:%M:%S"),
        remaining_balance=total_payable,
        status=BidStatus.PENDING,
    )

    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    db.refresh(account)

    return new_loan