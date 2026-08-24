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


import logging

logger = logging.getLogger(__name__)

async def _migrate_sqlite(conn) -> None:
    """Safely adds missing columns to existing SQLite tables."""
    # List of tables and the new columns they should have
    # Format: { table_name: [ (column_name, column_type, default_clause) ] }
    migrations = {
        "crops": [
            ("variety", "VARCHAR(100)", ""),
            ("yield_amount", "FLOAT", ""),
            ("yield_unit", "VARCHAR(20)", "DEFAULT 'kg'"),
        ],
        "irrigation_logs": [
            ("growth_stage", "VARCHAR(100)", ""),
        ],
        "disease_records": [
            ("outcome", "TEXT", ""),
        ],
    }

    for table, columns in migrations.items():
        # Check if table exists
        result = await conn.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not result.scalar():
            continue  # Table doesn't exist yet, create_all will handle it or it's not our concern

        # Get existing columns
        result = await conn.execute(f"PRAGMA table_info({table})")
        existing_cols = {row[1] for row in result.fetchall()}

        # Add missing columns
        for col_name, col_type, default_clause in columns:
            if col_name not in existing_cols:
                logger.info(f"Adding missing column '{col_name}' to table '{table}'")
                alter_stmt = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} {default_clause}"
                await conn.execute(alter_stmt)

async def init_db() -> None:
    """Create all tables. Used for dev/SQLite — production uses Alembic."""
    async with engine.begin() as conn:
        # First ensure all tables exist
        await conn.run_sync(Base.metadata.create_all)
        
        # Then safely migrate existing SQLite tables to add any missing columns
        if settings.is_sqlite:
            # We need to drop down to the raw connection for PRAGMA statements, or just use text()
            from sqlalchemy import text
            
            async def run_migrations(connection):
                # Format: { table_name: [ (column_name, column_type, default_clause) ] }
                migrations = {
                    "crops": [
                        ("variety", "VARCHAR(100)", ""),
                        ("yield_amount", "FLOAT", ""),
                        ("yield_unit", "VARCHAR(20)", "DEFAULT 'kg'"),
                    ],
                    "irrigation_logs": [
                        ("growth_stage", "VARCHAR(100)", ""),
                    ],
                    "disease_records": [
                        ("outcome", "TEXT", ""),
                    ],
                }

                for table, columns in migrations.items():
                    # Check if table exists
                    result = await connection.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"))
                    if not result.scalar():
                        continue

                    # Get existing columns
                    result = await connection.execute(text(f"PRAGMA table_info({table})"))
                    existing_cols = {row[1] for row in result.fetchall()}

                    # Add missing columns
                    for col_name, col_type, default_clause in columns:
                        if col_name not in existing_cols:
                            import logging
                            logging.getLogger(__name__).info(f"Migrating SQLite: Adding column '{col_name}' to table '{table}'")
                            alter_stmt = f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type} {default_clause}"
                            await connection.execute(text(alter_stmt))
                            
            await run_migrations(conn)
