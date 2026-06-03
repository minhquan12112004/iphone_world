from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config.settings import get_settings

settings = get_settings()

# Use DATABASE_URL from settings if provided, otherwise default to sqlite in app folder
DATABASE_URL = getattr(settings, "database_url", "sqlite:///./app/app.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create database tables. Call at app startup in development."""
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
