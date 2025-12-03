from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, DateTime

from app.database.db_config import Base


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # User
    public_key = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime , default=datetime.utcnow)

class Account(Base):
    __tablename__ = 'account'

    account_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
