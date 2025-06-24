"""
Database connection for the Zabbix AI Anomaly Detection application
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from ..core.config import DATABASE_URL
from .models import metadata, create_view_sql

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def get_db():
    """
    Get a database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize the database with required tables and views
    """
    try:
        # Create tables if they don't exist
        metadata.create_all(bind=engine)
        
        # Create view
        with engine.begin() as conn:
            conn.execute(text(create_view_sql))
        
        return True
    except SQLAlchemyError as e:
        print(f"Database initialization error: {e}")
        return False 