from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_directory(database_url: str) -> None:
    """Create the parent folder for a file-based SQLite DB when needed.

    This keeps local development simple and also prevents Render deploys from
    failing if DATABASE_URL points to a nested SQLite path such as
    sqlite:///./data/careflow.db. The default sqlite:///./careflow.db still works.
    """
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

    Base.metadata.create_all(bind=engine)
