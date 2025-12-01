from typing import Optional
from sqlalchemy.orm import Session
from models import Users

def get_user_by_username(db: Session, username: str) -> Optional[Users]:
    """
       Small helper to fetch a user by username.
       This is our first 'service' function that routers will call
       instead of querying the DB directly.
       """
    return db.query(Users).filter(Users.username == username).first()