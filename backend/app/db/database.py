import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base

# Determine Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_PASSWORD = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Sometimes people use password here, but typically we want a direct connection string
    
    # Default to local docker postgres if no env vars provided
    DATABASE_URL = "postgresql://postgres:password@localhost:5432/reconai"

# SQLAlchemy setup
# Note: we use sync engine for simpler integration unless specifically asked for async.
# The user asked for PostgreSQL-compatible persistence throughout.
try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    # We allow the engine creation to fail gracefully if the connection string is totally malformed
    engine = None
    SessionLocal = None
    print(f"Database initialization failed: {e}")

def get_db():
    if not SessionLocal:
        raise RuntimeError("Database is unavailable. Configure DATABASE_URL.")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    if engine:
        Base.metadata.create_all(bind=engine)
