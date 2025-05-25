# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import uuid

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
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

#
# A Schema stores all the configuration and business tables other than transactional ones.
BASE_SCHEMA = 'base_schema'


#
# Menu Unique ids
MENU_ADMINS_UNIQUE_ID = '9cc6115c-1ef5-4a42-8e51-f7e966d69808'
MENU_PLANS_UNIQUE_ID = '5cffabbf-fe0c-43df-ae77-b047e3d16d69'
MENU_COUPONS_UNIQUE_ID = '9c200036-b161-468b-8a51-262629dd0556'

#
# Role Unique ids
ROLE_ADMIN_UNIQUE_ID = '150bbe0e-5219-4054-93ca-e926b822646f'
ROLE_READONLY_UNIQUE_ID = '4e131a88-cd5d-4b09-8731-d2eb6a40a9ce'
ROLE_CONTENT_UNIQUE_ID = '68938ac9-1e51-4b2b-9fff-ded2c26fe46b'
ROLE_SUPPORT_UNIQUE_ID = '99a11632-992c-4834-8909-102a6906290e'
ROLE_OPERATIONS_UNIQUE_ID = 'd42c9282-861b-4198-806d-dd294a84946a'


YELLOW_ADMIN_USER_SLUG = '4004a730-cf97-4fdd-9ff1-610477d79b03'

YELLOW_ADMIN = {
    'name': 'Yellow Admin',
    'user_slug': YELLOW_ADMIN_USER_SLUG,
    'description': '',
    'password_hash': '$argon2id$v=19$m=102400,t=3,p=4$jZES4nwPwXgPYUypFeJcCw$cZlkKjQ6gCp2+Q23hzLxOTImtbfq5QevNGVyEa1opUg',
    'user_contact': {
        'category': 'EMAIL',
        'value': 'siva@getyellow.in'
    },
    'roles': [
        ROLE_ADMIN_UNIQUE_ID
    ]
}


MENU_ITEMS = [
    {
        'name': 'Admins',
        'menu_slug': MENU_ADMINS_UNIQUE_ID,
        'description': 'Manage Dashboard Users',
        'priority': 1,
        'is_active': 'Y',
        'children': [],
    },
    {
        'name': 'Plans',
        'menu_slug': MENU_PLANS_UNIQUE_ID,
        'description': 'Manage Plans',
        'priority': 2,
        'is_active': 'Y',
        'children': [],
    },
    {
        'name': 'Coupons',
        'menu_slug': MENU_COUPONS_UNIQUE_ID,
        'description': 'Manage Coupons',
        'priority': 3,
        'is_active': 'Y',
        'children': [],
    },
]


ROLE_N_MENU = [
    {
        'name': 'YELLOW-ADMIN',
        'role_slug': ROLE_ADMIN_UNIQUE_ID,
        'description': 'Role that to be assigned to Super Admininistrators',
        'is_active': 'Y',
        'menus': [
            {'menu_slug': MENU_ADMINS_UNIQUE_ID, 'can_read': True, 'can_write': True},
            {'menu_slug': MENU_PLANS_UNIQUE_ID, 'can_read': True, 'can_write': True},
            {'menu_slug': MENU_COUPONS_UNIQUE_ID, 'can_read': True, 'can_write': True},
        ]
    },
    {
        'name': 'CONTENT',
        'role_slug': ROLE_CONTENT_UNIQUE_ID,
        'description': 'Role that to be assigned to Content Staff',
        'is_active': 'Y',
        'menus': [
            {'menu_slug': MENU_ADMINS_UNIQUE_ID, 'can_read': False, 'can_write': False},
            {'menu_slug': MENU_PLANS_UNIQUE_ID, 'can_read': True, 'can_write': True},
            {'menu_slug': MENU_COUPONS_UNIQUE_ID, 'can_read': True, 'can_write': True},
        ]
    },
    {
        'name': 'SUPPORT',
        'role_slug': ROLE_SUPPORT_UNIQUE_ID,
        'description': 'Role that to be assigned to Support Staff',
        'is_active': 'Y',
        'menus': [
            {'menu_slug': MENU_ADMINS_UNIQUE_ID, 'can_read': False, 'can_write': False},
            {'menu_slug': MENU_PLANS_UNIQUE_ID, 'can_read': True, 'can_write': False},
            {'menu_slug': MENU_COUPONS_UNIQUE_ID, 'can_read': True, 'can_write': False},
        ]
    },
    {
        'name': 'OPERATIONS',
        'role_slug': ROLE_OPERATIONS_UNIQUE_ID,
        'description': 'Role that to be assigned to Operations Staff',
        'is_active': 'Y',
        'menus': [
            {'menu_slug': MENU_ADMINS_UNIQUE_ID, 'can_read': False, 'can_write': False},
            {'menu_slug': MENU_PLANS_UNIQUE_ID, 'can_read': False, 'can_write': False},
            {'menu_slug': MENU_COUPONS_UNIQUE_ID, 'can_read': False, 'can_write': False},
        ]
    },
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

    def create_or_update_role(self, yellow_admin, role_detail):

        #
        # WARNING: Local Import, do not move outside
        from core.db.models import MenuModel, RoleModel, MenuRoleModel

        role_item = self.session.query(
            RoleModel
        ).where(
            RoleModel.role_slug == role_detail['role_slug']
        ).one_or_none()

        if not role_item:
            role_item = RoleModel(
                role_slug=role_detail['role_slug'],
                name=role_detail['name'],
                description=role_detail['description'],
                updated_by=yellow_admin.user_id
            )
            self.session.add(role_item)
            self.session.flush()

        else:
            #
            # Update the existing menu item
            role_item.name = role_detail['name']
            role_item.description = role_detail['description']
            role_item.is_active = role_detail['is_active']
            role_item.updated_by = yellow_admin.user_id


        for menu in role_detail['menus']:

            menu_id = self.session.query(
                MenuModel.menu_id
            ).where(
                MenuModel.menu_slug == menu['menu_slug']
            ).scalar()

            menu_role_item = self.session.query(
                MenuRoleModel
            ).where(
                MenuRoleModel.menu_id == menu_id,
                MenuRoleModel.role_id == role_item.role_id,
                MenuRoleModel.is_active == 'Y',
            ).one_or_none()

            if not menu_role_item:
                menu_role_item = MenuRoleModel(
                    menu_id=menu_id,
                    role_id=role_item.role_id,
                    can_read=menu['can_read'],
                    can_write=menu['can_write'],
                    updated_by=yellow_admin.user_id,
                )
                self.session.add(menu_role_item)
                self.session.flush()

            else:
                menu_role_item.can_read = menu['can_read']
                menu_role_item.can_write = menu['can_write']
                menu_role_item.updated_by = yellow_admin.user_id

        return role_item

    def load_or_create_yellow_admin(self):

        #
        # WARNING: Local Import, do not move outside
        from core.db.models import UserModel, UserContactModel

        yellow_admin = self.session.query(
            UserModel
        ).where(
            UserModel.user_slug == YELLOW_ADMIN_USER_SLUG
        ).one_or_none()

        yellow_user_contact_detail = YELLOW_ADMIN['user_contact']

        if not yellow_admin:
            yellow_admin = UserModel(
                user_slug=YELLOW_ADMIN_USER_SLUG,
                name=YELLOW_ADMIN['name'],
                is_internal=True,
                is_verified=True,
                password_hash=YELLOW_ADMIN['password_hash'],
                password_expires_after='1999-12-31T23:59:59'  # Requires to reset the password Immediately
            )
            self.session.add(yellow_admin)
            self.session.flush()

        else:
            yellow_admin.name = YELLOW_ADMIN['name']

        yellow_user_contact = self.session.query(
            UserContactModel
        ).where(
            UserContactModel.user_id == yellow_admin.user_id,
            UserContactModel.category == yellow_user_contact_detail['category'],
            UserContactModel.value == yellow_user_contact_detail['value'],
        ).one_or_none()

        if not yellow_user_contact:
            yellow_user_contact = UserContactModel(
                user_id=yellow_admin.user_id,
                category=yellow_user_contact_detail['category'],
                value=yellow_user_contact_detail['value'],
                is_primary=True,
                is_verified=True,
                updated_by=yellow_admin.user_id,
            )
            self.session.add(yellow_user_contact)
            self.session.flush()

        return yellow_admin

    def create_or_update_menu_item(self, yellow_admin, menu_detail):

        #
        # WARNING: Local Import, do not move outside
        from core.db.models import MenuModel

        menu_item = self.session.query(
            MenuModel
        ).where(
            MenuModel.menu_slug == menu_detail['menu_slug']
        ).one_or_none()

        if not menu_item:
            menu_item = MenuModel(
                menu_slug=menu_detail['menu_slug'],
                name=menu_detail['name'],
                description=menu_detail['description'],
                priority=menu_detail['priority'],
                updated_by=yellow_admin.user_id
            )
            self.session.add(menu_item)
            self.session.flush()

        else:
            #
            # Update the existing menu item
            menu_item.name = menu_detail['name']
            menu_item.description = menu_detail['description']
            menu_item.priority = menu_detail['priority']
            menu_item.is_active = menu_detail['is_active']

        return menu_item

    def sync(self):

        #
        # WARNING: Local Import, do not move outside
        from core.db.models import UserRoleModel

        yellow_admin = self.load_or_create_yellow_admin()

        menu_obj_map = dict()
        for menu_detail in MENU_ITEMS:
            menu_item = self.create_or_update_menu_item(yellow_admin=yellow_admin, menu_detail=menu_detail)
            menu_obj_map[str(menu_item.menu_slug)] = menu_item

        role_obj_map = dict()
        for role_detail in ROLE_N_MENU:
            role_item = self.create_or_update_role(yellow_admin=yellow_admin, role_detail=role_detail)
            role_obj_map[str(role_item.role_slug)] = role_item

        #
        # Add roles to YELLOW_ADMIN user
        for role_slug in YELLOW_ADMIN['roles']:
            user_role = self.session.query(
                UserRoleModel
            ).where(
                UserRoleModel.is_active == 'Y',
                UserRoleModel.user_id == yellow_admin.user_id,
                UserRoleModel.role_id == role_obj_map[role_slug].role_id,
            ).one_or_none()

            if not user_role:
                user_role = UserRoleModel(
                    user_id=yellow_admin.user_id,
                    role_id=role_obj_map[role_slug].role_id,
                    updated_by=yellow_admin.user_id,
                )
                self.session.add(user_role)
                self.session.flush()


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
