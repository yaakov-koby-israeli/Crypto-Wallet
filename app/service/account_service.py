from app.database.models import Account, Users
from app.service.web3_service import get_account_balance
from sqlalchemy.orm import Session

def setup_account_for_user(db: Session, user: Users) -> Account:

    """
    Create a new account for the user based on real on-chain balance.
    """

    # Check existing account
    existing_account = db.query(Account).filter(Account.user_id == user.id).first()
    if existing_account:
        raise ValueError("Account already exists")

    # Read blockchain balance
    real_balance = get_account_balance(user.public_key)

    new_account = Account(
        user_id=user.id,
        balance=real_balance,
        is_active=True
    )

    db.add(new_account)
    db.commit()
    db.refresh(new_account)

    return new_account

def update_db_after_transfer_eth(db: Session, from_account: Account, to_account: Account, amount: float):
    from_account.balance -= amount
    to_account.balance += amount
    db.commit()
    db.refresh(from_account)
    db.refresh(to_account)
