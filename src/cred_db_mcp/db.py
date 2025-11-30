import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Default to a local file for dev/test if not specified
DB_PATH = os.getenv("DB_PATH", "credentialwatch.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# specific check for checks that might run in different environments
if DB_PATH == ":memory:":
    DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    """Dependency for FastAPI to get a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Helper to initialize the DB (create tables)."""
    Base.metadata.create_all(bind=engine)
