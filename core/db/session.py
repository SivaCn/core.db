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
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from contextlib import asynccontextmanager

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import (
    AsyncSession,

    create_async_engine,
)
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.constants import (
    const_db,
)

from core.utils.helpers.environ import (
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


async def get_tenant_session(db_config, verbose=False):

    conn_str = const_db.DATABASE_URL.format(
        **{
            'dialect': const_db.READ_WRITE_DB_URL_DIALECT,
            **db_config
        }
    )

    engine = create_async_engine(
        conn_str,
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        future=True,
        echo=verbose,
    )

    # Session Makers
    _AsyncSession = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    return _AsyncSession()


async def get_tenant_master_session(tenant, verbose=False):

    tenant_db_config = {
        'host': tenant.master_db_host,
        'port': tenant.master_db_port,
        'db_name': tenant.master_db_name,
        'username': tenant.master_db_username,
        'password': tenant.master_db_password,
    }

    return await get_tenant_session(tenant_db_config, verbose=verbose)


async def get_tenant_replica_session(tenant, verbose=False):

    tenant_db_config = {
        'host': tenant.replica_db_host,
        'port': tenant.replica_db_port,
        'db_name': tenant.replica_db_name,
        'username': tenant.replica_db_username,
        'password': tenant.replica_db_password,
    }

    return await get_tenant_session(tenant_db_config, verbose=verbose)


@asynccontextmanager
async def get_db_sessions(workspace: Optional[str] = None):
    """Provides both master and replica database sessions."""

    #
    # NOTE: Do not move this import outside
    from core.db.statements import stmt_query_tenant_config

    meta_master_session: AsyncSession = AsyncSessionLocalMetaMaster()
    meta_replica_session: AsyncSession = AsyncSessionLocalMetaReplica()

    tenant_master_session = None
    tenant_replica_session = None

    try:

        if workspace:
            tenant_cursor = await meta_master_session.execute(
                stmt_query_tenant_config(workspace=workspace)
            )
            tenant = tenant_cursor.scalar_one_or_none()
            if not tenant:
                raise RuntimeError(f"Unable to get tenant details for '{workspace}'")

            tenant_master_session = await get_tenant_master_session(tenant, verbose=db_config.verbose)
            tenant_replica_session = await get_tenant_replica_session(tenant, verbose=db_config.verbose)

        yield DotDict(
            {
                "meta_write": meta_master_session,
                "meta_read": meta_replica_session,
                "tenant_write": tenant_master_session,
                "tenant_read": tenant_replica_session,
            }
        )

        await meta_master_session.commit()

        if tenant_master_session:
            await tenant_master_session.commit()

        if tenant_replica_session:
            await tenant_replica_session.commit()

    except Exception:
        await meta_master_session.rollback()

        if tenant_master_session:
            await tenant_master_session.rollback()

        if tenant_replica_session:
            await tenant_replica_session.rollback()

        raise

    finally:
        await meta_master_session.close()
        await meta_replica_session.close()

        if tenant_master_session:
            await tenant_master_session.close()

        if tenant_replica_session:
            await tenant_replica_session.close()


class ScopedSession:

    def __init__(self, db_config):
        self.session = self.get_session(db_config)

    def get_session(self, db_config):

        if not isinstance(db_config, dict):
            raise Exception(f"Expecting argument db_config of type dict, Got '{type(db_config).__name__}'")

        conn_str = const_db.DATABASE_URL.format(
            **{
                'dialect': const_db.MIGRATION_DB_URL_DIALECT,
                **db_config
            }
        )

        engine = create_engine(conn_str, poolclass=NullPool)
        Session = sessionmaker(bind=engine)

        return Session()

    def __enter__(self):
        return self.session

    def __exit__(self, *args, **kwargs):
        #
        # make a clean commit to the session.
        self.session.commit()

        #
        # attempt for a clean closing of the session.
        self.session.close()

