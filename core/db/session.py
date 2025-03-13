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
from alembic.config import Config

from contextlib import asynccontextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,

    create_async_engine,
)
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.constants import const_db

from core.utils.helpers.environ import (
    get_build_path,
    get_build_config,
)

from core.utils.helpers.utils import (
    DotDict,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


POOL_SIZE = 10  # Number of connections in the pool
MAX_OVERFLOW = 5  # Allow extra connections temporarily


alembic_config_path = os.path.join(
    get_build_path(), 'files', 'config', 'migrations.ini'
)

if not os.path.exists(alembic_config_path):
    raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")

alembic_cfg = Config(alembic_config_path)

database_url = alembic_cfg.get_main_option('sqlalchemy.url')

db_config = get_build_config(section='database')

DB_MASTER_URL = database_url.format(
    **{
        'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
        **db_config.master.as_dict()
    }
)

DB_REPLICA_URL = database_url.format(
    **{
        'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
        **db_config.replica.as_dict()
    }
)

# Master Database Engine (Read & Write)
master_engine = create_async_engine(
    DB_MASTER_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    future=True,
    echo=True
)

# Replica Database Engine (Read-Only)
replica_engine = create_async_engine(
    DB_REPLICA_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    future=True,
    echo=True
)

# Session Makers
AsyncSessionLocalMaster = sessionmaker(
    bind=master_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class ReadOnlySession(AsyncSession):
    def add(self, *args, **kwargs):
        raise RuntimeError("Cannot add objects on a read-only session!")

    def flush(self, *args, **kwargs):
        raise RuntimeError("Cannot flush on a read-only session!")

    def commit(self, *args, **kwargs):
        raise RuntimeError("Cannot commit on a read-only session!")

AsyncSessionLocalReplica = sessionmaker(
    bind=replica_engine,
    class_=ReadOnlySession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_db_sessions():
    """Provides both master and replica database sessions."""

    master_session: AsyncSession = AsyncSessionLocalMaster()
    replica_session: AsyncSession = AsyncSessionLocalReplica()

    try:
        yield DotDict(
            {"master": master_session, "replica": replica_session}
        )
        await master_session.commit()

    except Exception:
        await master_session.rollback()
        raise

    finally:
        await master_session.close()
        await replica_session.close()

