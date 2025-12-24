from fastapi import Depends, HTTPException, status, APIRouter, WebSocket, WebSocketDisconnect
from app.database.models import Users, Account
from typing import Annotated
from sqlalchemy.orm import Session
from dependencies.database_dependency import get_db
from dependencies.user_dependency import get_current_user
from app.schemas.transfer_request import TransferRequest
from app.service.account_service import setup_account_for_user, update_db_after_transfer_eth
from app.service.web3_service import GanacheUnavailableError, ensure_account_exists_on_ganache, get_account_balance_from_blockchain, get_transactions_for_address, send_eth
from app.service.websocket_manager import manager


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
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
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
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError:
        raise HTTPException(status_code=400, detail="Account already exists")

    return {
        "message": "Account set up successfully",
        "account_id": new_account.account_id,
        "balance": new_account.balance,
    }

@router.get("/user-transactions", status_code=status.HTTP_200_OK)
async def list_transactions(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    public_key = user.get("public_key")
    if not public_key:
        raise HTTPException(status_code=400, detail="User does not have a public key set")

    try:
        txs = get_transactions_for_address(public_key) or []
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Build address -> username lookup for nicer display
    addresses: set[str] = set()
    for tx in txs:
        if tx.get("from"):
            addresses.add(tx["from"])
        if tx.get("to"):
            addresses.add(tx["to"])

    users = db.query(Users).all()
    addr_to_username = {
        user.public_key.lower(): user.username
        for user in users
        if user.public_key
    }

    for tx in txs:
        from_addr = (tx.get("from") or "").lower()
        to_addr_raw = tx.get("to") or ""
        to_addr = to_addr_raw.lower() if to_addr_raw else ""

        tx["from_username"] = addr_to_username.get(from_addr, tx.get("from"))
        tx["to_username"] = addr_to_username.get(
            to_addr,
            "External/Contract" if to_addr_raw else "External/Contract",
        )

    return {"transactions": txs}

@router.get("/account", status_code=status.HTTP_200_OK)
async def get_account(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    db_account = db.query(Account).filter(Account.user_id == user.get("id")).first()
    if not db_account:
        return {"balance": 0, "account_id": None}

    public_key = user.get("public_key")
    if not public_key:
        raise HTTPException(status_code=400, detail="User does not have a public key set")

    try:
        chain_balance = get_account_balance_from_blockchain(public_key)
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_account.balance = chain_balance
    db.commit()
    db.refresh(db_account)

    return {"balance": db_account.balance, "account_id": db_account.account_id}

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)

### transfer Eth endpoints ###

@router.post("/transfer-eth", status_code=status.HTTP_200_OK)
async def transfer_eth(user: user_dependency, db: db_dependency, transfer_request: TransferRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')
    
    to_account = db.query(Account).filter(Account.account_id == transfer_request.to_account).first()
    if not to_account:
        raise HTTPException(status_code=404, detail='Destination Account not found')

    from_account = db.query(Account).filter(Account.user_id == user.get("id")).first()
    if not from_account:
        raise HTTPException(status_code=404, detail='User account not found')

    if from_account.account_id == to_account.account_id:
        raise HTTPException(status_code=404, detail='You cant send ETH to yourself (:')

    public_key = user.get("public_key")
    if not public_key:
        raise HTTPException(status_code=400, detail="User does not have a public key set")

    try:
        curr_user_balance = get_account_balance_from_blockchain(public_key)
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if transfer_request.amount > curr_user_balance:
        raise HTTPException(status_code=400, detail='Insufficient balance on chain')

    to_account_user = db.query(Users).filter(Users.id == to_account.user_id).first()
    if not to_account_user:
        raise HTTPException(status_code=404, detail='Destination User Not Found')
    
    # Ensure the provided username matches the destination account owner
    if to_account_user.username != transfer_request.recipient_username:
        raise HTTPException(
            status_code=400,
            detail='Account ID does not match the provided username',
        )

    # Use web3 service to transfer the money
    try:
        tx_hash = send_eth(
            from_address=public_key,
            to_address=to_account_user.public_key,
            amount=transfer_request.amount,
        )
    except GanacheUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException (status_code=400 , detail=f"{e}")

    # Update user who delivers the eth
    update_db_after_transfer_eth(db, public_key, from_account)

    # Update user who gets the eth
    update_db_after_transfer_eth(db, to_account_user.public_key , to_account)

    await manager.send_personal_message("update_balance", to_account_user.id)

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
