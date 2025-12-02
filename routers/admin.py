from fastapi import Depends, HTTPException, status, APIRouter, Path
from sqlalchemy.orm import Session
from app.database.models import Users, Account
from typing import Annotated
from app.database.session_local import get_db
from routers.auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)


db_dependency = Annotated [Session,Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/users", status_code=status.HTTP_200_OK)
async def read_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':  # Fixed "user_role" to "role"
        raise HTTPException(status_code=403, detail="Unauthorized Access")
    return db.query(Users).all()

@router.get("/accounts", status_code=status.HTTP_200_OK)
async def read_all_accounts(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':  # Fixed "user_role" to "role"
        raise HTTPException(status_code=403, detail="Unauthorized Access")
    return db.query(Account).all()

@router.delete("/delete-user/{user_id}", status_code=status.HTTP_200_OK)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):

    if user is None or user.get('role') != 'admin':  # Fixed "user_role" to "role"
        raise HTTPException(status_code=403, detail="Unauthorized Access")

    # Fetch user and account associated with user_id
    user_to_delete = db.query(Users).filter(Users.id == user_id).first()
    user_account_to_delete = db.query(Account).filter(Account.user_id == user_id).first()

    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User Not Found!")

    # Delete user and associated account in a single transaction
    db.delete(user_account_to_delete)
    db.commit()  # Single commit for both operations

    return {"message": f"User {user_id} and associated account deleted successfully"}

