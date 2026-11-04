import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.app.config import DATABASE_URL, DB_ENABLED
from .models import Base

logger = logging.getLogger("uvicorn.error")

engine = None
SessionLocal = None

if DB_ENABLED and DATABASE_URL:
    try:
        # pool_pre_ping automatically recovers from disconnected DB connections
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            connect_args={"connect_timeout": 5}
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        logger.warning(f"[DB] Could not configure database engine: {e}")
        engine = None
        SessionLocal = None

def is_db_connected() -> bool:
    """Check if the PostgreSQL database is live and reachable."""
    if not engine:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            return True
    except Exception:
        return False

def init_db() -> bool:
    """Create all PostgreSQL tables if database is connected."""
    if not is_db_connected():
        logger.info("[DB] PostgreSQL is offline or unreachable. Running in local JSON storage mode.")
        return False
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("[DB] PostgreSQL tables verified and ready.")
        return True
    except Exception as e:
        logger.error(f"[DB] Error creating database tables: {e}")
        return False

def get_db():
    """FastAPI dependency for obtaining a database session."""
    if not SessionLocal:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
