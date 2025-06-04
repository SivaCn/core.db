# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import uuid

from typing import List, Optional
from collections import namedtuple
from datetime import datetime, UTC
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import pytz

import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import CreateColumn
from sqlalchemy.ext.compiler import compiles

from sqlalchemy.dialects.postgresql import UUID
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.constants import (
    const_business,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

#
# A Schema stores all the configuration and business tables other than transactional ones.
BASE_SCHEMA = 'base_schema'


Role = namedtuple(
    'Role',
    ['name', 'role_slug', 'description']
)

AdminUser = namedtuple(
    'AdminUser',
    ['name', 'admin_slug', 'email', 'password_hash', 'password_algo', 'is_super', 'roles']
)

MenuRole = namedtuple(
    'MenuRole',
    ['role', 'can_read', 'can_write']
)


MenuItem = namedtuple(
    'MenuItem',
    ['name', 'description', 'menu_slug', 'priority', 'roles', 'is_active', 'children']
)


def role(name: str,
         role_slug: str,
         description: Optional[str] = None):

    return Role(name=name, role_slug=role_slug, description=description)


def admin_user(name: str,
               admin_slug: str,
               email: str,
               password_hash: str,
               password_algo: str,
               roles: List[Role],
               is_super: bool = False):

    return AdminUser(
        name=name,
        admin_slug=admin_slug,
        email=email,
        password_hash=password_hash,
        password_algo=password_algo,
        is_super=is_super,
        roles=roles
    )


def menu_item(name: str,
              menu_slug: str,
              priority: int,
              roles: List[MenuRole],
              description: Optional[str] = None,
              is_active: Optional[bool] = True,
              children: Optional[List[MenuItem]] = None):

    return MenuItem(
        name=name,
        description=description,
        menu_slug=menu_slug,
        priority=priority,
        roles=roles,
        is_active=is_active,
        children=children,
    )


#
# NOTE: Add new Roles here
ROLE_SUPER_ADMIN = 'SUPER-ADMIN'
ROLE_ADMIN = 'ADMIN'
ROLE_CONTENT = 'CONTENT'


ROLES = {
    ROLE_SUPER_ADMIN: role(name=ROLE_SUPER_ADMIN, role_slug='150bbe0e-5219-4054-93ca-e926b822646f'),
    ROLE_ADMIN: role(name=ROLE_ADMIN, role_slug='d42c9282-861b-4198-806d-dd294a84946a'),
    ROLE_CONTENT: role(name=ROLE_CONTENT, role_slug='68938ac9-1e51-4b2b-9fff-ded2c26fe46b'),
}


SUPER_ADMIN = admin_user(
    name='Yellow Super Admin',
    admin_slug='7cc64cc3-cc16-4a9f-8a8e-83fbb2a21991',
    email='admin.eng@getyellow.in',
    password_hash='$argon2id$v=19$m=102400,t=3,p=4$jZES4nwPwXgPYUypFeJcCw$cZlkKjQ6gCp2+Q23hzLxOTImtbfq5QevNGVyEa1opUg',
    password_algo='',
    is_super=True,
    roles=[
        ROLES[ROLE_SUPER_ADMIN]
    ]
)

MENU_ITEMS = [
    menu_item(
        name='Admins',
        menu_slug='f7a5df85-5ab9-4241-8c44-1fa44e1d30ee',
        priority=1,
        roles=[
            MenuRole(role=ROLES[ROLE_SUPER_ADMIN], can_read=True, can_write=True),
            MenuRole(role=ROLES[ROLE_ADMIN], can_read=True, can_write=True),
        ],
        is_active=True,
        children=None
    ),
    menu_item(
        name='Plans',
        menu_slug='117d15da-81f6-4dc5-a95c-ff527f672212',
        priority=2,
        roles=[
            MenuRole(role=ROLES[ROLE_SUPER_ADMIN], can_read=True, can_write=True),
            MenuRole(role=ROLES[ROLE_ADMIN], can_read=True, can_write=True),
            MenuRole(role=ROLES[ROLE_CONTENT], can_read=True, can_write=True),
        ],
        is_active=True,
        children=None
    ),
    menu_item(
        name='Coupons',
        menu_slug='8cba4c27-3535-4bb1-8ed8-5757b50c43c7',
        priority=3,
        roles=[
            MenuRole(role=ROLES[ROLE_SUPER_ADMIN], can_read=True, can_write=True),
            MenuRole(role=ROLES[ROLE_ADMIN], can_read=True, can_write=True),
            MenuRole(role=ROLES[ROLE_CONTENT], can_read=True, can_write=True),
        ],
        is_active=True,
        children=None
    )
]


class SyncUserAndRoles:
    """This script syncs the user, roles and menu. this must be invoked from the DB Migrations file

    Example usage: REV_AA_0017_sync_user_and_roles.py

    Usage:

        #
        # HINT: in the upgrade method of migration, use as shown below
        #

        def upgrade() -> None:

            # Get the current connection
            connection = op.get_bind()

            # create a session from connection
            from sqlalchemy.orm import sessionmaker
            from core.db.alembic import SyncUserAndRoles

            Session = sessionmaker(bind=connection)
            session = Session()

            try:
                SyncUserAndRoles(session=session).sync()

            except Exception as error:
                raise Exception(
                    f'Hint: This script might have failed now '
                    f'as there coule be updates in the underlying sync script '
                    f'You may need to add backward compatibilty or just suppress this error '
                    f'ERROR DETAIL: {error}'
                )

    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def sync_roles(self):

        #
        # XXX: Method level Imports
        from core.db.models.meta import RoleModel

        roles = dict()
        for role_name, role_detail in ROLES.items():

            role = self.session.query(
                RoleModel
            ).where(
                RoleModel.role_slug == role_detail.role_slug
            ).one_or_none()

            if not role:
                role = RoleModel(
                    name=role_detail.name,
                    role_slug=role_detail.role_slug,
                    description=role_detail.description,
                )
                self.session.add(role)
                self.session.flush()

            if role and role.is_active != const_business.IS_ACTIVE_YES:
                #
                # Reactivate the role if in-active
                role.is_active = const_business.IS_ACTIVE_YES

            roles[role_name] = role

        return roles

    def sync_admin_users(self, roles):

        #
        # XXX: Method level imports
        from core.db.models.meta import AdminModel, AdminRoleModel

        admin = self.session.query(
            AdminModel
        ).where(
            AdminModel.admin_slug == SUPER_ADMIN.admin_slug
        ).one_or_none()

        if not admin:
            #
            # Insist the Admin to reset the password Immediately
            expire_after = datetime.now(UTC).replace(minute=0, hour=0, second=0, microsecond=0, tzinfo=None)

            admin = AdminModel(
                name=SUPER_ADMIN.name,
                admin_slug=SUPER_ADMIN.admin_slug,
                email=SUPER_ADMIN.email,
                is_accepted=True,
                password_hash=SUPER_ADMIN.password_hash,
                password_algo=SUPER_ADMIN.password_algo,
                password_expires_after=expire_after,
            )
            self.session.add(admin)
            self.session.flush()

        if admin and admin.is_active != const_business.IS_ACTIVE_YES:
            admin.is_active = const_business.IS_ACTIVE_YES

        role_obj = [
            role.role_id
            for _, role in roles.items()
            if str(role.role_slug) == SUPER_ADMIN.roles[0].role_slug
        ]

        if not role_obj:
            raise Exception("Unable to resolve role for the Super Admin")

        admin_role = self.session.query(
            AdminRoleModel
        ).where(
            AdminRoleModel.admin_id == admin.admin_id,
            AdminRoleModel.role_id == role_obj[0],
            AdminRoleModel.is_active == const_business.IS_ACTIVE_YES,
        ).one_or_none()

        if not admin_role:
            admin_role = AdminRoleModel(
                admin_id=admin.admin_id,
                role_id=role_obj[0],
            )
            self.session.add(admin_role)
            self.session.flush()

    def sync_menu(self, roles):

        #
        # XXX: Method level imports
        from core.db.models.meta import MenuModel, MenuRoleModel

        role_map = {role.name: role.role_id for _, role in roles.items()}

        for menu_item in MENU_ITEMS:
            menu = self.session.query(
                MenuModel
            ).where(
                MenuModel.menu_slug == menu_item.menu_slug
            ).one_or_none()

            menu.priority = menu_item.priority
            menu.is_active = const_business.IS_ACTIVE_YES

            if not menu:
                menu = MenuModel(
                    name=menu_item.name,
                    menu_slug=menu_item.menu_slug,
                    description=menu_item.description,
                    parent_id=None,  ## Support to be added when Menu Nesting is required
                    priority=menu_item.priority,
                )
                self.session.add(menu)
                self.session.flush()

            for menu_role_detail in menu_item.roles:
                menu_role = self.session.query(
                    MenuRoleModel
                ).where(
                    MenuRoleModel.menu_id == menu.menu_id,
                    MenuRoleModel.role_id == role_map[menu_role_detail.role.name],
                ).one_or_none()

                if menu_role:
                    menu_role.can_read = menu_role_detail.can_read
                    menu_role.can_write = menu_role_detail.can_write

                else:
                    menu_role = MenuRoleModel(
                        menu_id=menu.menu_id,
                        role_id=role_map[menu_role_detail.role.name],
                        can_read=menu_role_detail.can_read,
                        can_write=menu_role_detail.can_write,
                    )
                    self.session.add(menu_role)
                    self.session.flush()

    def sync(self):
        roles = self.sync_roles()
        self.sync_admin_users(roles)
        self.sync_menu(roles)


@compiles(CreateColumn, 'postgresql')
def use_identity(element, compiler, **kwargs):

    return compiler.visit_create_column(
        element, **kwargs
    ).replace("SERIAL", "INT GENERATED BY DEFAULT AS IDENTITY")


def utc_now():
    """Helper function to ensure UTC datetime."""
    return datetime.now(pytz.utc)


def field_slug(field_name: str):
    """Helper function for common unique_id field for table creation."""
    return sa.Column(
        field_name,
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        server_default=sa.text("gen_random_uuid()")
    )

def field_is_active():
    """Helper function for common is_active field for table creation."""
    return sa.Column(
        'is_active',
        sa.String(1),
        server_default=sa.text("'Y'"),
        nullable=False
    )


def field_updated_by():
    """Helper function for common updated_by field for table creation."""
    return sa.Column(
        'updated_by',
        sa.BigInteger,
        nullable=True
    )


def field_created_date():
    """Helper function for common created_date field for table creation."""
    return sa.Column(
        'created_date',
        sa.DateTime(timezone=False),
        nullable=False,
        server_default=sa.text("TIMEZONE('UTC', now())")
    )


def field_updated_date():
    """Helper function for common updated_date field for table creation."""
    return sa.Column(
        'updated_date',
        sa.DateTime(timezone=False),
        nullable=False,
        server_default=sa.text("TIMEZONE('UTC', now())"),
        onupdate=utc_now
    )


def field_hist_slug(field_name: str):
    """Helper function for common unique_id field for table creation."""
    return sa.Column(field_name, UUID(as_uuid=True), nullable=True)


def field_hist_is_active():
    """Helper function for common is_active field for table creation."""
    return sa.Column('is_active', sa.String(1), nullable=True)


def field_hist_updated_by():
    """Helper function for common updated_by field for table creation."""
    return sa.Column('updated_by', sa.BigInteger, nullable=True)


def field_hist_created_date():
    """Helper function for common created_date field for table creation."""
    return sa.Column('created_date', sa.DateTime(timezone=False), nullable=True)


def field_hist_updated_date():
    """Helper function for common updated_date field for table creation."""
    return sa.Column('updated_date', sa.DateTime(timezone=False), nullable=True)


model_slug = field_slug
model_is_active = field_is_active
model_updated_by = field_updated_by


def model_created_date():
    """Helper function common created_date field.

    Note: Use this for Models always
    """
    return sa.Column(
        sa.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False
    )


def model_updated_date():
    """Helper function common updated_date field.

    Note: Use this for Models always
    """
    return sa.Column(
        sa.DateTime,
        default=lambda: datetime.now(UTC).replace(tzinfo=None),
        onupdate=lambda: datetime.now(UTC).replace(tzinfo=None),
        nullable=False
    )
