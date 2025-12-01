from fastapi import Depends, HTTPException, status, APIRouter
from models import Users, Account, Loans
from database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from routers.auth import get_current_user
from enums import BidStatus
from app.schemas.transfer_request import TransferRequest
from app.schemas.loan_request import LoanRequest
from app.schemas.repay_loan_request import RepayLoanRequest
from app.service.account_service import setup_account_for_user, update_db_after_transfer_eth
from app.service.web3_service import get_account_balance, send_eth
from app.service.loan_service import request_loan_for_account

router = APIRouter(
    prefix='/user',
    tags=['user']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

                                                  #### End Points ####

@router.get("/my-loan", status_code=status.HTTP_200_OK)
async def get_my_loan(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Find the user's account
    account = db.query(Account).filter(Account.user_id == user.get("id")).first()
    if not account:
        raise HTTPException(status_code=404, detail="User does not have an account")

    # Find the loan linked to the user's account
    loan = db.query(Loans).filter(Loans.account_id == account.account_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="No loan found for this user")

    return {
        "loan_id": loan.loan_id,
        "amount": loan.amount,
        "interest_rate": loan.interest_rate.value,  # Convert Enum to value
        "duration_months": loan.duration_months.value,  # Convert Enum to value
        "start_date": loan.start_date,
        "end_date": loan.end_date,
        "remaining_balance": loan.remaining_balance,
        "status": loan.status.value,  # Convert Enum to string
        "borrower_active_loan": account.active_loan  # Show if borrower still has an active loan
    }

@router.post("/set-up-account", status_code=status.HTTP_201_CREATED)
async def set_up_account(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Convert dict user → ORM user object
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    #try to create new account
    try:
        new_account = setup_account_for_user(db, db_user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Account already exists")

    return {
        "message": "Account set up successfully",
        "account_id": new_account.account_id,
        "balance": new_account.balance,
    }

                                          ### transfer Eth endpoints ###

@router.post("/transfer-eth", status_code=status.HTTP_201_CREATED)
async def transfer_eth(user: user_dependency, db: db_dependency, transfer_request: TransferRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    from_account = db.query(Account).filter(Account.user_id == user.get("id")).first()
    to_account = db.query(Account).filter(Account.account_id == transfer_request.to_account).first()

    if not from_account or not to_account:
        raise HTTPException(status_code=404, detail='Account not found')

    if transfer_request.amount > from_account.balance:
        raise HTTPException(status_code=400, detail='Insufficient balance')

    to_account_user = db.query(Users).filter(to_account.user_id == Users.id).first()
    if not to_account_user:
        raise HTTPException(status_code=404, detail='Destination User Not Found')

    # Use web3 service instead of direct web3 ganache
    tx_hash = send_eth(
        from_address=user.get("public_key"),
        to_address=to_account_user.public_key,
        amount=transfer_request.amount,
    )

    # Update account balances in database
    update_db_after_transfer_eth(db,from_account,to_account,transfer_request.amount)

    return {"message": "ETH transferred successfully", "transaction_hash": tx_hash}


                                            ### Loan Management ###

@router.post("/request-loan", status_code=status.HTTP_201_CREATED)
async def request_loan(user: user_dependency, db: db_dependency, loan_request: LoanRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # patch user details (row)
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        new_loan = request_loan_for_account(db, db_user, loan_request)
    except ValueError  as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "message": "Loan request submitted successfully",
        "loan_id": new_loan.loan_id,
        "total_repayment": new_loan.remaining_balance,
        # "installment_amount": installment_amount TODO add How much loaner needs to pay every month in loans db
    }

@router.post("/repay-loan/{loan_id}")
async def repay_loan(user: user_dependency, db: db_dependency, loan_id: int, request: RepayLoanRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # Extract user_payment from request body
    user_payment = request.user_payment

    # Fetch the loan
    loan = db.query(Loans).filter(Loans.loan_id == loan_id, Loans.status == BidStatus.APPROVED).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found or not approved")

    if user_payment <= 0:
        raise HTTPException(status_code=400, detail="Invalid repayment amount")

    # Fetch the borrower's account
    account = db.query(Account).filter(Account.account_id == loan.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Borrower's account not found")

    if user_payment > account.balance:
        raise HTTPException(status_code=400, detail="Insufficient balance for repayment")

    # Fetch the admin's account (loan provider - Bank)
    admin_account = db.query(Account).filter(Account.user_id == 1).first()
    if not admin_account:
        raise HTTPException(status_code=404, detail="Admin's account not found")

    # Fetch the admin User (loan provider - Bank)
    admin_user = db.query(Users).filter(Users.id == 1).first()
    if not admin_user:
        raise HTTPException(status_code=404, detail="Admin User not found")

    # checking if user paid more then he needs if user
    if loan.remaining_balance < user_payment:
        raise HTTPException(status_code=400, detail=f"User need to pay only {loan.remaining_balance}eth !")

    # Transfer ETH from borrower to admin using transfer_eth FIRST
    transfer_request = TransferRequest(
        to_account=admin_account.account_id,
        amount=user_payment
    )

    transfer_response = await transfer_eth(user, db, transfer_request)  # Call the existing transfer function
    if "transaction_hash" not in transfer_response:
        raise HTTPException(status_code=500, detail="Loan transfer failed on the blockchain")

    new_user_balance = get_account_balance(user.get("public_key"))
    account.balance = new_user_balance

    # Update Loan Details
    loan.remaining_balance -= user_payment

    # Prevent negative balance
    if loan.remaining_balance < 0:
        loan.remaining_balance = 0

    # If loan is fully paid, mark as Paid
    if loan.remaining_balance <= 0:
        loan.remaining_balance = 0
        loan.status = BidStatus.PAID  # Loan is now fully paid
        account.active_loan = False

    db.commit()  # Save changes to the database
    db.refresh(loan)
    db.refresh(account)
    db.refresh(admin_account)

    return {
        "message": "Repayment successful",
        "remaining_balance": loan.remaining_balance,
        "transaction_hash": transfer_response["transaction_hash"]
    }

@router.delete("/delete-account", status_code=status.HTTP_200_OK)
async def delete_account(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    # Check if the user already has an account
    existing_account_to_delete = db.query(Account).filter(Account.user_id == user.get("id")).first()
    if not existing_account_to_delete:
        raise HTTPException(status_code=400, detail='User Dont Have an Account')

    db.delete(existing_account_to_delete)
    db.commit()  # Single commit for both operations

    return {"message": "Account Deleted successfully", "user_id": user.get("id")}