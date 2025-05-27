# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import os
import re
import string
import argparse
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.constants import const_db, const_business

from core.utils.helpers.environ import (
    ConsoleScript,
    get_build_path,
    get_build_config,
)

from core.db.session import ScopedSession

from core.db.models.meta import TenantConfigModel
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


def increment_revision(revision: str) -> str:
    """
    Increment a revision string of the format 'REV_XX_NNNN'.

    The function:
    - Increments the numeric part (NNNN) by 1.
    - If the numeric part reaches '9999', it resets to '0000' and increments the letter sequence (XX).
    - The letter sequence follows alphabetical ordering ('AA' -> 'AB' -> ... -> 'ZZ').

    Args:
        revision (str): The current revision string (e.g., 'REV_AA_0000').

    Returns:
        str: The next revision string (e.g., 'REV_AA_0001' or 'REV_AB_0000' if overflow occurs).

    Raises:
        ValueError: If the input format is incorrect or exceeds 'REV_ZZ_9999'.
    """

    def increment_letters(letters: str) -> str:
        """
        Increment a two-letter sequence (AA, AB, ..., ZZ).

        Args:
            letters (str): The current two-letter code (e.g., 'AA').

        Returns:
            str: The next letter sequence (e.g., 'AB', 'AC', ..., 'ZZ').

        Raises:
            ValueError: If the letters exceed 'ZZ'.
        """
        if letters == "ZZ":
            raise ValueError("Maximum revision limit 'REV_ZZ_9999' reached.")

        alphabet = string.ascii_uppercase
        first, second = letters

        if second == 'Z':
            first = alphabet[alphabet.index(first) + 1]
            second = 'A'
        else:
            second = alphabet[alphabet.index(second) + 1]

        return first + second

    prefix, letters, number = revision.split('_')

    if prefix != "REV" or len(letters) != 2 or not number.isdigit():
        raise ValueError("Invalid revision format. Expected format: 'REV_XX_NNNN'.")

    num = int(number) + 1

    if num > 9999:
        num = 0  # Reset number
        letters = increment_letters(letters)

    return f"REV_{letters}_{num:04d}"


# @ConsoleScript
# def apply_migrations():
#
#     parser = argparse.ArgumentParser(description="Database Migration Script.")
#
#     group = parser.add_mutually_exclusive_group(required=True)
#
#     group.add_argument("--upgrade", action="store_true", help="Upgrade to the latest version")
#     group.add_argument("--current", action="store_true", help="Show the current version")
#     group.add_argument("--downgrade", action="store_true", help="Downgrade to a previous version")
#     group.add_argument("--new-revision", type=str, help="Adds a new Migrtaion Revision")
#
#     args = parser.parse_args()
#
#     alembic_config_path = os.path.join(
#         get_build_path(), 'files', 'config', 'migrations.ini'
#     )
#
#     if not os.path.exists(alembic_config_path):
#         raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")
#
#     alembic_cfg = Config(alembic_config_path)
#
#     database_url = alembic_cfg.get_main_option('sqlalchemy.url')
#
#     db_config = get_build_config(section='database')
#
#     alembic_cfg.set_main_option(
#         'sqlalchemy.url',
#         database_url.format(
#             **{
#                 'dialect': const_db.MIGRATION_DB_URL_DIALECT,
#                 **db_config.master.as_dict()
#             }
#         )
#     )
#
#     if args.upgrade:
#         command.upgrade(alembic_cfg, 'head')
#
#     elif args.current:
#         command.current(alembic_cfg)
#
#     elif args.downgrade:
#         command.downgrade(alembic_cfg, '-1')
#
#     elif args.new_revision:
#         current_revision = ScriptDirectory.from_config(alembic_cfg).get_current_head()
#         new_revision = increment_revision(current_revision)
#         command.revision(alembic_cfg, args.new_revision, rev_id=new_revision)


@ConsoleScript
def apply_meta_migrations():

    parser = argparse.ArgumentParser(description="Database Migration Script.")

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--upgrade", action="store_true", help="Upgrade to the latest version")
    group.add_argument("--current", action="store_true", help="Show the current version")
    group.add_argument("--downgrade", action="store_true", help="Downgrade to a previous version")
    group.add_argument("--new-revision", type=str, help="Adds a new Migrtaion Revision")

    args = parser.parse_args()

    alembic_config_path = os.path.join(
        get_build_path(), 'files', 'config', 'migrations.ini'
    )

    if not os.path.exists(alembic_config_path):
        raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")

    alembic_cfg = Config(alembic_config_path)

    database_url = alembic_cfg.get_main_option('sqlalchemy.url')

    db_config = get_build_config(section='database')

    alembic_cfg.set_main_option(
        'script_location', os.path.join(get_build_path(), 'migrations', 'meta')
    )

    alembic_cfg.set_main_option(
        'sqlalchemy.url',
        database_url.format(
            **{
                'dialect': const_db.MIGRATION_DB_URL_DIALECT,
                **db_config.master.as_dict()
            }
        )
    )

    if args.upgrade:
        command.upgrade(alembic_cfg, 'head')

    elif args.current:
        command.current(alembic_cfg)

    elif args.downgrade:
        command.downgrade(alembic_cfg, '-1')

    elif args.new_revision:
        current_revision = ScriptDirectory.from_config(alembic_cfg).get_current_head()
        new_revision = increment_revision(current_revision)
        command.revision(alembic_cfg, args.new_revision, rev_id=new_revision)


def migrations(args, category):
    """Generic Migration function."""

    if category not in ('meta', 'tenant', ):
        raise Exception(f"Unsupported category: '{category}'")

    alembic_config_path = os.path.join(
        get_build_path(), 'files', 'config', 'migrations.ini'
    )

    if not os.path.exists(alembic_config_path):
        raise FileNotFoundError(f"File '{alembic_config_path}' does not exist !")

    alembic_cfg = Config(alembic_config_path)

    database_url = alembic_cfg.get_main_option('sqlalchemy.url')

    db_config = get_build_config(section='database')

    with ScopedSession(db_config.master.as_dict()) as meta_session:

        if args.new_revision and args.workspace == 'ALL':
            raise Exception(f"New Revision Cannot be applied to all Workspaces")

        stmt = meta_session.query(
            TenantConfigModel
        ).where(
            TenantConfigModel.is_active == const_business.IS_ACTIVE_YES
        )

        if args.workspace != 'ALL':
            #
            # Apply Tenant level Restrictions
            stmt = stmt.where(TenantConfigModel.workspace == args.workspace)

        tenants = stmt.all()

        for tenant in tenants:

            print(f"\n\nWorking with Tenant: '{tenant.workspace}' <<<\n")

            tenant_db_config = {
                'host': tenant.master_db_host,
                'port': tenant.master_db_port,
                'db_name': tenant.master_db_name,
                'username': tenant.master_db_username,
                'password': tenant.master_db_password,
            }


            alembic_cfg.set_main_option(
                'script_location', os.path.join(get_build_path(), 'migrations', category)
            )

            alembic_cfg.set_main_option(
                'sqlalchemy.url',
                database_url.format(
                    **{
                        'dialect': const_db.MIGRATION_DB_URL_DIALECT,
                        **tenant_db_config,
                    }
                )
            )

            if args.upgrade:
                command.upgrade(alembic_cfg, 'head')

            elif args.current:
                command.current(alembic_cfg)

            elif args.downgrade:
                command.downgrade(alembic_cfg, '-1')

            elif args.new_revision:
                current_revision = ScriptDirectory.from_config(alembic_cfg).get_current_head()
                new_revision = increment_revision(current_revision)
                command.revision(alembic_cfg, args.new_revision, rev_id=new_revision)

            print(f"\n>>> Completed Tenant: {tenant}")


@ConsoleScript
def apply_tenant_migrations():

    parser = argparse.ArgumentParser(description="Database Migration Script.")

    parser.add_argument('--workspace', type=str, required=True, help='Workspace ID (required)')

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument("--upgrade", action="store_true", help="Upgrade to the latest version")
    group.add_argument("--current", action="store_true", help="Show the current version")
    group.add_argument("--downgrade", action="store_true", help="Downgrade to a previous version")
    group.add_argument("--new-revision", type=str, help="Adds a new Migrtaion Revision")

    args = parser.parse_args()

    migrations(args, category='tenant')

