# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
from typing import Optional
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


db_config = get_build_config(section='database')

DB_MASTER_URL = const_db.DATABASE_URL.format(
    **{
        'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
        **db_config.master.as_dict()
    }
)

DB_REPLICA_URL = const_db.DATABASE_URL.format(
    **{
        'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
        **db_config.replica.as_dict()
    }
)

# Master Database Engine (Read & Write)
meta_master_engine = create_async_engine(
    DB_MASTER_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    future=True,
    echo=db_config.verbose,
)

# Replica Database Engine (Read-Only)
meta_replica_engine = create_async_engine(
    DB_REPLICA_URL,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    future=True,
    echo=db_config.verbose,
)

# Session Makers
AsyncSessionLocalMetaMaster = sessionmaker(
    bind=meta_master_engine,
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


AsyncSessionLocalMetaReplica = sessionmaker(
    bind=meta_replica_engine,
    class_=ReadOnlySession,
    expire_on_commit=False
)


@asynccontextmanager
async def get_db_sessions(workspace: Optional[str] = None):
    """Provides both master and replica database sessions."""

    meta_master_session: AsyncSession = AsyncSessionLocalMetaMaster()
    meta_replica_session: AsyncSession = AsyncSessionLocalMetaReplica()

    if workspace:
        pass

    try:
        yield DotDict(
            {"meta_write": meta_master_session, "meta_read": meta_replica_session}
        )
        await meta_master_session.commit()

    except Exception:
        await meta_master_session.rollback()
        raise

    finally:
        await meta_master_session.close()
        await meta_replica_session.close()

