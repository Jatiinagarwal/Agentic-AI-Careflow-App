from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_directory(database_url: str) -> None:
    if not database_url.startswith("sqlite"):
        return
    url = make_url(database_url)
    database_path = url.database
    if not database_path or database_path == ":memory:":
        return
    path = Path(database_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)


settings = get_settings()
_ensure_sqlite_directory(settings.database_url)

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models so SQLAlchemy registers all tables before create_all.
    from app import models  # noqa: F401

    # Hackathon-friendly schema upgrade: if a pre-Phase-9 SQLite DB exists, reset it
    # because this project uses mock data and seed data is recreated on startup.
    inspector = inspect(engine)
    if settings.database_url.startswith("sqlite") and inspector.has_table("patients"):
        patient_columns = {column["name"] for column in inspector.get_columns("patients")}
        required_columns = {"email", "risk_level", "status", "preferred_language"}
        if not required_columns.issubset(patient_columns):
            Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
