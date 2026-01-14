import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from configuration.config import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base = sqlalchemy.orm.declarative_base()

def create_tables():
    Base.metadata.create_all(bind=engine)
