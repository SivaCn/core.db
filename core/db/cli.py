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



def apply_migrations():

    alembic_config_path = os.path.join(
        get_build_path(), 'files', 'config', 'migrations.ini'
    )

    if not os.path.exists(alembic_config_path):
        raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")

    alembic_cfg = Config(alembic_config_path)

    database_url = alembic_cfg.get_main_option('sqlalchemy.url')

    db_config = get_build_config(section='database')

    alembic_cfg.set_main_option(
        'sqlalchemy.url',
        database_url.format(
            **{
                'dialect': const_db.MIGRATION_DB_URL_DIALECT,
                **db_config.master.as_dict()
            }
        )
    )

    import pdb; pdb.set_trace()  # TODO: Remove This line
    command.upgrade(alembic_cfg, 'head')

