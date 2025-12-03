from fastapi import Depends, HTTPException, status, APIRouter, Path
from sqlalchemy.orm import Session
from app.database.models import Users, Account
from typing import Annotated
from dependencies.database_dependency import get_db
from dependencies.user_dependency import get_current_user

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
    if user_to_delete is None:
        raise HTTPException(status_code=404, detail="User Not Found!")

    # Fetch account associated with user_id
    user_account_to_delete = db.query(Account).filter(Account.user_id == user_id).first()
    if user_account_to_delete is None:
        raise HTTPException(status_code=404, detail="User Account Not Found!")

    db.delete(user_to_delete)  # This deletes account too thanks to CASCADE
    db.commit()

    return {"message": f"User {user_id} and associated account deleted successfully"}

