import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from .models import Base

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://user:password@postgres:5432/mydb')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db_session = scoped_session(SessionLocal)

def init_db():
    """Initialize the database, creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get a database session."""
    db = db_session()
    try:
        yield db
    finally:
        db.close()