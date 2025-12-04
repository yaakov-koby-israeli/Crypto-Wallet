from fastapi import Depends, HTTPException, status, APIRouter
from app.database.models import Users, Account
from typing import Annotated
from sqlalchemy.orm import Session
from dependencies.database_dependency import get_db
from dependencies.user_dependency import get_current_user
from app.schemas.transfer_request import TransferRequest
from app.service.account_service import setup_account_for_user, update_db_after_transfer_eth
from app.service.web3_service import ensure_account_exists_on_ganache, get_account_balance_from_blockchain, get_transactions_for_address, send_eth


router = APIRouter(
    prefix='/user',
    tags=['user']
)

db_dependency = Annotated [Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

 #### End Points ####

@router.post("/set-up-account", status_code=status.HTTP_201_CREATED)
async def set_up_account(user: user_dependency, db: db_dependency, public_key: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    try:
        ensure_account_exists_on_ganache(public_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Convert dict user to ORM user object
    db_user = db.query(Users).filter(Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.public_key = public_key
    db.commit()
    db.refresh(db_user)

    # try to create new account
    try:
        new_account = setup_account_for_user(db, db_user)
    except ValueError:
        raise HTTPException(status_code=400, detail="Account already exists")

    return {
        "message": "Account set up successfully",
        "account_id": new_account.account_id,
        "balance": new_account.balance,
    }

@router.get("/user-transactions", status_code=status.HTTP_200_OK)
async def list_transactions(user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    public_key = user.get("public_key")
    if not public_key:
        raise HTTPException(status_code=400, detail="User does not have a public key set")

    try:
        txs = get_transactions_for_address(public_key)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"transactions": txs}

### transfer Eth endpoints ###

@router.post("/transfer-eth", status_code=status.HTTP_200_OK)
async def transfer_eth(user: user_dependency, db: db_dependency, transfer_request: TransferRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    from_account = db.query(Account).filter(Account.user_id == user.get("id")).first()
    if not from_account :
        raise HTTPException(status_code=404, detail='User account not found')

    to_account = db.query(Account).filter(Account.account_id == transfer_request.to_account).first()
    if not to_account:
        raise HTTPException(status_code=404, detail='Destination Account not found')

    curr_user_balance = get_account_balance_from_blockchain(user.get("public_key"))

    if transfer_request.amount > curr_user_balance:
        raise HTTPException(status_code=400, detail='Insufficient balance on chain')

    to_account_user = db.query(Users).filter(Users.id == to_account.user_id).first()
    if not to_account_user:
        raise HTTPException(status_code=404, detail='Destination User Not Found')

    # Use web3 service to transfer the money
    try:
        tx_hash = send_eth(
            from_address=user.get("public_key"),
            to_address=to_account_user.public_key,
            amount=transfer_request.amount,
        )
    except ValueError as e:
        raise HTTPException (status_code=400 , detail=f"{e}")

    # Update user who delivers the eth
    update_db_after_transfer_eth(db,user.get("public_key"),from_account)

    # Update user who gets the eth
    update_db_after_transfer_eth(db, to_account_user.public_key , to_account)

    return {"message": "ETH transferred successfully", "transaction_hash": tx_hash}

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
