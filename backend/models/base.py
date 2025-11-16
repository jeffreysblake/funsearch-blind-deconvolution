"""Base database model and session management."""

from datetime import datetime
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Will be configured from config
DATABASE_URL = "sqlite:///funsearch.db"


class Base(DeclarativeBase):
    """Base class for all database models."""

    pass


# Engine and session factory (will be initialized by app)
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite specific
    echo=False,  # Set to True for SQL logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency.

    Yields:
        Database session

    Usage:
        def some_function(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database (create all tables)."""
    Base.metadata.create_all(bind=engine)


def reset_db() -> None:
    """Drop and recreate all tables (for testing)."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
