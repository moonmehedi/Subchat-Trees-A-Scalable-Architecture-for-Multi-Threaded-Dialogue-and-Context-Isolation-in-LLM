"""
Database Package

Contains database configuration, session management, and utilities
for the hierarchical chat research backend.
"""

from typing import Generator

# Import errors expected until dependencies are installed
try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.exc import SQLAlchemyError
except ImportError:
    create_engine = None
    sessionmaker = None
    Session = None
    SQLAlchemyError = Exception

from app.core.config import settings
from app.models.database_models import Base, create_all_tables


# ============================================================================
# DATABASE ENGINE SETUP
# ============================================================================

# Create database engine with research-optimized settings
engine = None
SessionLocal = None

if create_engine and sessionmaker:
    try:
        engine = create_engine(
            settings.effective_database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            echo=settings.database_echo,
            # Research-specific optimizations
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=3600,   # Recycle connections every hour
        )
        
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False  # Keep objects accessible after commit
        )
        
        print(f"✅ Database engine created: {settings.effective_database_url}")
        
    except Exception as e:
        print(f"❌ Database engine creation failed: {e}")


# ============================================================================
# DATABASE SESSION MANAGEMENT
# ============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI endpoints.
    
    Provides database session with proper cleanup and error handling
    for research data persistence.
    
    Yields:
        Session: SQLAlchemy database session
    """
    if not SessionLocal:
        raise RuntimeError("Database not configured")
    
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        db.rollback()
        print(f"Database error: {e}")
        raise
    except Exception as e:
        db.rollback()
        print(f"Unexpected error: {e}")
        raise
    finally:
        db.close()


def create_database_tables():
    """
    Create all database tables for the research backend.
    
    This function ensures all models are created in the database
    with proper research schema and relationships.
    """
    if not engine:
        print("❌ Cannot create tables: Database engine not available")
        return False
    
    try:
        create_all_tables(engine)
        print("✅ Database tables created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False


def check_database_connection() -> bool:
    """
    Check database connectivity for health monitoring.
    
    Returns:
        bool: True if database is accessible, False otherwise
    """
    if not engine:
        return False
    
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")
        return True
        
    except Exception as e:
        print(f"Database connectivity check failed: {e}")
        return False


# ============================================================================
# RESEARCH DATA UTILITIES
# ============================================================================

def get_database_stats() -> dict:
    """
    Get database statistics for research monitoring.
    
    Returns:
        dict: Database statistics including table counts and sizes
    """
    if not engine:
        return {"error": "Database not available"}
    
    try:
        with engine.connect() as connection:
            # Get table information
            if settings.effective_database_url.startswith("sqlite"):
                # SQLite queries
                tables_query = "SELECT name FROM sqlite_master WHERE type='table'"
                result = connection.execute(tables_query)
                tables = [row[0] for row in result]
                
                stats = {"database_type": "SQLite", "tables": {}}
                for table in tables:
                    count_query = f"SELECT COUNT(*) FROM {table}"
                    result = connection.execute(count_query)
                    count = result.scalar()
                    stats["tables"][table] = {"count": count}
                    
            else:
                # PostgreSQL queries
                stats = {"database_type": "PostgreSQL", "tables": {}}
                # Would implement PostgreSQL-specific queries here
        
        return stats
        
    except Exception as e:
        return {"error": f"Database stats failed: {e}"}


def cleanup_research_data(session_id: str, older_than_days: int = 30) -> bool:
    """
    Cleanup old research data for session management.
    
    Args:
        session_id: Session identifier to cleanup
        older_than_days: Remove data older than this many days
        
    Returns:
        bool: Success status
    """
    if not SessionLocal:
        return False
    
    try:
        from datetime import datetime, timedelta
        from app.models.database_models import ResearchAnalytics, VectorDocument
        
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        db = SessionLocal()
        
        # Cleanup old analytics data
        analytics_deleted = db.query(ResearchAnalytics).filter(
            ResearchAnalytics.session_id == session_id,
            ResearchAnalytics.measurement_timestamp < cutoff_date
        ).delete()
        
        # Cleanup old vector documents (optional)
        vectors_deleted = db.query(VectorDocument).filter(
            VectorDocument.session_id == session_id,
            VectorDocument.timestamp < cutoff_date,
            VectorDocument.is_active == False
        ).delete()
        
        db.commit()
        db.close()
        
        print(f"Cleaned up {analytics_deleted} analytics and {vectors_deleted} vectors for session {session_id}")
        return True
        
    except Exception as e:
        print(f"Research data cleanup failed: {e}")
        return False


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def initialize_database():
    """
    Initialize database for the research backend.
    
    This function sets up the database, creates tables, and performs
    initial configuration for the research environment.
    """
    print("🔧 Initializing research database...")
    
    # Create tables
    if create_database_tables():
        print("✅ Database tables initialized")
    else:
        print("❌ Database table initialization failed")
        return False
    
    # Check connectivity
    if check_database_connection():
        print("✅ Database connectivity verified")
    else:
        print("❌ Database connectivity verification failed")
        return False
    
    # Display database stats
    stats = get_database_stats()
    if "error" not in stats:
        print(f"📊 Database type: {stats.get('database_type', 'Unknown')}")
        print(f"📊 Tables created: {len(stats.get('tables', {}))}")
    
    print("🔬 Research database ready for hierarchical chat innovations!")
    return True


# ============================================================================
# EXPORT UTILITIES
# ============================================================================

__all__ = [
    "engine",
    "SessionLocal", 
    "get_db",
    "create_database_tables",
    "check_database_connection",
    "get_database_stats",
    "cleanup_research_data",
    "initialize_database"
]
