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


# Singleton engine — created once at module import
_engine: Optional[Engine] = None
_session_maker: Optional[sessionmaker] = None


def get_engine(db_url: Optional[str] = None, **kwargs) -> Engine:
    """
    Return the singleton SQLAlchemy Engine.
    Created once on first call, reused for all subsequent calls.
    """
    global _engine
    if _engine is None:
        url = db_url or settings.DATABASE_URL or "sqlite:///./counterguard.db"
        connect_args = kwargs.pop("connect_args", {})

        is_sqlite = url.startswith("sqlite")
        if is_sqlite and "check_same_thread" not in connect_args:
            connect_args["check_same_thread"] = False

        _engine = create_engine(url, connect_args=connect_args, **kwargs)

        if is_sqlite:
            event.listen(_engine, "connect", _set_sqlite_pragma)

    return _engine


def get_session_maker(
    engine: Optional[Engine] = None, db_url: Optional[str] = None
) -> sessionmaker[Session]:
    """
    Return the singleton sessionmaker.
    Created once on first call, reused for all subsequent calls.
    """
    global _session_maker
    if _session_maker is None:
        eng = engine or get_engine(db_url)
        _session_maker = sessionmaker(bind=eng, autoflush=False, expire_on_commit=False)
    return _session_maker


def get_db_session() -> Generator[Session, None, None]:
    """
    Generator function yielding a scoped SQLAlchemy Session.
    Ideal for FastAPI Dependency Injection and unit of work context handling.
    """
    session_maker = get_session_maker()
    session = session_maker()
    try:
        yield session
    except Exception as e:
        session.rollback()
        logger.error(f"Database session rollback triggered due to error: {e}")
        raise
    finally:
        session.close()
