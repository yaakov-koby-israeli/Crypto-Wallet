from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.models import Users
from dependencies.database_dependency import get_db
from routers.auth import get_current_user as get_current_user_token

async def get_current_user(
    token_user: dict = Depends(get_current_user_token),
    db: Session = Depends(get_db),
):
    if token_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    user_id = token_user.get("id")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")

    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    return {
        "username": db_user.username,
        "id": db_user.id,
        "role": db_user.role,
        "public_key": db_user.public_key,
    }
