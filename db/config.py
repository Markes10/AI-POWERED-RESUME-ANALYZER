"""
Database configuration settings and connection management.
Uses PostgreSQL via SQLAlchemy with SQLite fallback for local dev.
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db_pool():
    """Initialize database connection and create tables."""
    try:
        from db.models import (
            User, Resume, Job, JobMatch, Interview, PerformanceReview,
            LearningPath, AttendanceRecord, CompensationRecord, DiversityMetric,
        )
        Base.metadata.create_all(bind=engine)
        print("Database tables created/verified successfully!")
        return True
    except Exception as e:
        print(f"Warning: Database init failed: {e}")
        print("Continuing without database (dev mode).")
        return False


def get_db_connection():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e


def close_db_connection(connection):
    """Close a database session."""
    if connection:
        connection.close()


def get_db():
    """Yield a SQLAlchemy session (FastAPI dependency style)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
