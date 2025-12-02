from fastapi import Depends, HTTPException, status, APIRouter
from app.database.models import Users, Account
from typing import Annotated
from sqlalchemy.orm import Session
from app.database.session_local import get_db
from routers.auth import get_current_user
from app.schemas.transfer_request import TransferRequest
from app.service.account_service import setup_account_for_user, update_db_after_transfer_eth
from app.service.web3_service import send_eth


router = APIRouter(
    prefix='/user',
    tags=['user']
)

db_dependency = Annotated [Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

 #### End Points ####

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

    # Use web3 service to transfer the money
    tx_hash = send_eth(
        from_address=user.get("public_key"),
        to_address=to_account_user.public_key,
        amount=transfer_request.amount,
    )

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