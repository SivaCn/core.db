# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import os
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from alembic import command
from alembic.config import Config

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.constants import const_db

from core.utils.helpers.environ import (
    get_build_path,
    get_build_config,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


alembic_config_path = os.path.join(
    get_build_path(), 'files', 'config', 'migrations.ini'
)

if not os.path.exists(alembic_config_path):
    raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")

alembic_cfg = Config(alembic_config_path)

database_url = alembic_cfg.get_main_option('sqlalchemy.url')

db_config = get_build_config(section='database')


@asynccontextmanager
async def get_write_session():
    """Dependency to get a write (primary) database session."""

    db_write_url = database_url.format(
        **{
            'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
            **db_config.master.as_dict()
        }
    )
    engine_write = create_async_engine(db_write_url, echo=True)
    SessionLocalWrite = async_sessionmaker(bind=engine_write, class_=AsyncSession, expire_on_commit=False)

    session = SessionLocalWrite()
    try:
        yield session
        await session.commit()  # Commit only write transactions
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


@asynccontextmanager
async def get_read_session():
    """Dependency to get a read (replica) database session."""

    db_read_url = database_url.format(
        **{
            'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
            **db_config.replica.as_dict()
        }
    )
    engine_read = create_async_engine(db_read_url, echo=True)
    SessionLocalRead = async_sessionmaker(bind=engine_read, class_=AsyncSession, expire_on_commit=False)

    session = SessionLocalRead()
    try:
        yield session  # No commit for read-only replica
    finally:
        await session.close()

