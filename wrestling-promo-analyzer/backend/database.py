"""
Database connection and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from config import settings

# ============================================================================
# DATABASE ENGINE
# ============================================================================

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Connection pool size
    max_overflow=10,  # Allow up to 10 extra connections
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for ORM models
Base = declarative_base()


# ============================================================================
# DEPENDENCY INJECTION
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session
            pass
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """
    Initialize database
    - Create all tables from models
    - Should be called on application startup
    """
    # Import all models so they are registered with Base
    import models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")


def drop_db():
    """
    Drop all database tables
    WARNING: This will delete all data!
    Only use in development/testing
    """
    if settings.APP_ENV == "production":
        raise RuntimeError("Cannot drop database in production!")

    Base.metadata.drop_all(bind=engine)
    print("⚠️  All database tables dropped")


# ============================================================================
# DATABASE HEALTH CHECK
# ============================================================================

def check_db_connection() -> bool:
    """
    Check if database connection is working

    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        db = SessionLocal()
        # Try to execute a simple query
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_table_names() -> list:
    """Get list of all table names in database"""
    return Base.metadata.tables.keys()


def get_row_count(table_name: str) -> int:
    """Get row count for a specific table"""
    db = SessionLocal()
    try:
        result = db.execute(f"SELECT COUNT(*) FROM {table_name}")
        return result.scalar()
    except Exception as e:
        print(f"Error getting row count for {table_name}: {e}")
        return -1
    finally:
        db.close()


# ============================================================================
# STARTUP VALIDATION
# ============================================================================

def validate_database():
    """
    Validate database connection and schema on startup
    """
    print("Validating database connection...")

    # Check connection
    if not check_db_connection():
        raise RuntimeError("Database connection failed!")

    print("✅ Database connection successful")

    # Check if tables exist
    db = SessionLocal()
    try:
        result = db.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        )
        tables = [row[0] for row in result]

        expected_tables = ["users", "videos", "transcripts", "judges", "analyses", "processing_jobs"]
        missing_tables = [t for t in expected_tables if t not in tables]

        if missing_tables:
            print(f"⚠️  Missing tables: {missing_tables}")
            print("Run: docker-compose exec backend python -c 'from database import init_db; init_db()'")
        else:
            print(f"✅ All expected tables exist: {', '.join(expected_tables)}")
    except Exception as e:
        print(f"⚠️  Could not validate tables: {e}")
    finally:
        db.close()


# ============================================================================
# TESTING HELPERS
# ============================================================================

def clear_all_data():
    """
    Clear all data from all tables
    WARNING: This will delete all data but keep tables!
    Only use in development/testing
    """
    if settings.APP_ENV == "production":
        raise RuntimeError("Cannot clear data in production!")

    db = SessionLocal()
    try:
        # Import models
        from models import ProcessingJob, Analysis, Transcript, Video, User, Judge

        # Delete in correct order (respecting foreign keys)
        db.query(ProcessingJob).delete()
        db.query(Analysis).delete()
        db.query(Transcript).delete()
        db.query(Video).delete()
        db.query(User).delete()
        # Don't delete judges - they are seed data

        db.commit()
        print("⚠️  All data cleared from database")
    except Exception as e:
        db.rollback()
        print(f"❌ Error clearing data: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # If run directly, initialize database
    print("Initializing database...")
    validate_database()
    init_db()
    print("Database initialization complete!")
