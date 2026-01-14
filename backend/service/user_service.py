from typing import Optional
from database.models import Users
from sqlalchemy.orm import Session

def get_user_by_username(db: Session, username: str) -> Optional[Users]:
    """
       Small helper to fetch a user by username.
       This is our first 'service' function that routers will call
       instead of querying the DB directly.
       """
    return db.query(Users).filter(Users.username == username).first()
