"""
AgriNova AI — Database engine & session management.

Provides async SQLAlchemy engine, session factory, and Base class.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ── Engine ──
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    # SQLite needs this to allow async access from multiple coroutines
    **({"connect_args": {"check_same_thread": False}} if settings.is_sqlite else {}),
)

# ── Session Factory ──
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


# ── Declarative Base ──
class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


async def get_db() -> AsyncSession:
    """FastAPI dependency — yields an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables. Used for dev/SQLite — production uses Alembic."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
