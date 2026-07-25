import logging
from typing import Generator, Optional

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from backend.settings import settings

logger = logging.getLogger(__name__)


def _set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enable foreign keys enforcement for SQLite connections.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(db_url: Optional[str] = None, **kwargs) -> Engine:
    """
    Create and return a SQLAlchemy database Engine.
    Defaults to settings.DATABASE_URL or SQLite fallback if none is specified.
    """
    url = db_url or settings.DATABASE_URL or "sqlite:///./counterguard.db"
    connect_args = kwargs.pop("connect_args", {})

    # If SQLite, add specific check_same_thread=False parameter and attach pragma listener
    is_sqlite = url.startswith("sqlite")
    if is_sqlite and "check_same_thread" not in connect_args:
        connect_args["check_same_thread"] = False

    engine = create_engine(url, connect_args=connect_args, **kwargs)

    if is_sqlite:
        event.listen(engine, "connect", _set_sqlite_pragma)

    return engine


def get_session_maker(
    engine: Optional[Engine] = None, db_url: Optional[str] = None
) -> sessionmaker[Session]:
    """
    Create and return a configured sessionmaker for creating database Sessions.
    """
    if engine is None:
        engine = get_engine(db_url)
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session(engine: Optional[Engine] = None) -> Generator[Session, None, None]:
    """
    Generator function yielding a scoped SQLAlchemy Session.
    Ideal for FastAPI Dependency Injection and unit of work context handling.
    """
    session_maker = get_session_maker(engine)
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session rollback triggered due to error: {e}")
        raise
    finally:
        session.close()
