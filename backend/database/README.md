# CounterGuard Database Layer

This module implements the persistent storage architecture for CounterGuard using **SQLAlchemy 2.0** and the **Repository Pattern**. It adheres strictly to **Clean Architecture**, **SOLID principles**, and **Dependency Injection**.

## Architecture Overview

1. **Database Abstraction & Support**
   - Initially configured for SQLite (`sqlite:///./counterguard.db`), complete with automatic `PRAGMA foreign_keys = ON` activation.
   - Built on SQLAlchemy 2.0 abstraction, enabling immediate transition to PostgreSQL simply by updating the `DATABASE_URL` environment variable without code or query modifications.

2. **Session & Connection Management (`engine.py`)**
   - `get_engine(db_url)`: Configures and returns an SQLAlchemy Engine.
   - `get_session_maker(engine)`: Provides a configured session factory with disabled autoflush and `expire_on_commit=False` for detached domain usage.
   - `get_db_session(engine)`: Dependency generator that yields a scoped database session, managing automatic transaction rollback on failure and session closing. Designed for FastAPI Dependency Injection.

3. **Repository Pattern (`repositories/`)**
   - Repository interfaces (`interfaces.py`) isolate business services from SQL mechanics and ORM specifics.
   - All concrete repositories accept an injected SQLAlchemy `Session` instance in their constructor (`__init__(self, session: Session)`).
   - Promotes loose coupling and simplifies unit testing via in-memory SQLite (`sqlite:///:memory:`).