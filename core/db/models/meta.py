# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import sqlalchemy as sa

from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.config import (
    BASE_SCHEMA,
)

from core.db.alembic import (
    #
    # Reusable Table Fields
    model_slug,
    model_is_active,
    model_updated_by,
    model_created_date,
    model_updated_date,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


# Define the base class for SQLAlchemy models
DeclarativeBase = declarative_base()


class TenantConfigModel(DeclarativeBase):

    __tablename__ = "tenant_config"
    __table_args__ = {"schema": BASE_SCHEMA}

    tenant_config_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tenant_config_slug = model_slug(field_name='tenant_config_slug')
    name = sa.Column(sa.String(128), nullable=False)
    workspace = sa.Column(sa.String(128), nullable=False)

    master_db_host = sa.Column(sa.String(128), nullable=True)
    master_db_port = sa.Column(sa.String(128), nullable=True)
    master_db_name = sa.Column(sa.String(128), nullable=True)
    master_db_username = sa.Column(sa.String(128), nullable=True)
    master_db_password = sa.Column(sa.String(128), nullable=True)

    replica_db_host = sa.Column(sa.String(128), nullable=True)
    replica_db_port = sa.Column(sa.String(128), nullable=True)
    replica_db_name = sa.Column(sa.String(128), nullable=True)
    replica_db_username = sa.Column(sa.String(128), nullable=True)
    replica_db_password = sa.Column(sa.String(128), nullable=True)

    storage_bucket = sa.Column(sa.String(64), nullable=False)

    is_migrated = sa.Column(sa.Boolean, nullable=False, default=False)

    theme = sa.Column(sa.JSON, nullable=False, default=dict)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class RoleModel(DeclarativeBase):

    __tablename__ = "role"
    __table_args__ = {"schema": BASE_SCHEMA}

    role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    role_slug = model_slug(field_name='role_slug')
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1024), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class AdminModel(DeclarativeBase):

    __tablename__ = "admin"
    __table_args__ = {"schema": BASE_SCHEMA}

    admin_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    admin_slug = model_slug(field_name='admin_slug')

    name = sa.Column(sa.String(128), nullable=False)
    email = sa.Column(sa.String(128), nullable=False)

    dob = sa.Column('dob', sa.Date, nullable=True)
    gender = sa.Column('gender', sa.String(16), nullable=True)

    is_accepted = sa.Column(sa.Boolean, nullable=False)
    password_hash = sa.Column(sa.String(1024), nullable=False)
    password_algo = sa.Column(sa.String(1024), nullable=True)
    password_expires_after = sa.Column( sa.DateTime(timezone=False), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class AdminRoleModel(DeclarativeBase):

    __tablename__ = "admin_role"
    __table_args__ = {"schema": BASE_SCHEMA}

    admin_role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    admin_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.admin.admin_id"), nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.role.role_id"), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class AdminInviteModel(DeclarativeBase):

    __tablename__ = "admin_invite"
    __table_args__ = {"schema": BASE_SCHEMA}

    admin_invite_id = sa.Column('admin_invite_id', sa.Integer, primary_key=True, autoincrement=True)
    admin_invite_slug = model_slug(field_name='admin_invite_slug')

    token = sa.Column(sa.String(10240), nullable=False)
    admin_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.admin.admin_id"), nullable=False)
    roles = sa.Column(postgresql.ARRAY(sa.String), nullable=False)
    status = sa.Column(sa.String(64), nullable=False)
    expires_after = sa.Column(sa.DateTime, nullable=False)
    invited_by = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.admin.admin_id"), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Menu model
class MenuModel(DeclarativeBase):

    __tablename__ = "menu"
    __table_args__ = {"schema": BASE_SCHEMA}

    menu_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    menu_slug = model_slug(field_name='menu_slug')
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1024), nullable=True)
    parent_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.menu.menu_id"), nullable=True)
    priority = sa.Column(sa.Integer, nullable=False, default=1)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Menu Role model
class MenuRoleModel(DeclarativeBase):

    __tablename__ = "menu_role"
    __table_args__ = {"schema": BASE_SCHEMA}

    menu_role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    menu_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.menu.menu_id"), nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.role.role_id"), nullable=False)

    can_read = sa.Column(sa.Boolean, nullable=False, default=False)
    can_write = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class SmsProviderModel(DeclarativeBase):

    __tablename__ = "sms_provider"
    __table_args__ = {"schema": BASE_SCHEMA}

    sms_provider_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    sms_provider_slug = model_slug(field_name='sms_provider_slug')
    name = sa.Column(sa.String(128), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class SmsProviderConfigModel(DeclarativeBase):

    __tablename__ = "sms_provider_config"
    __table_args__ = {"schema": BASE_SCHEMA}

    sms_provider_config_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    sms_provider_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(f"{BASE_SCHEMA}.sms_provider.sms_provider_id"),
        nullable=False
    )

    config_type = sa.Column(sa.String(128), nullable=False)
    key = sa.Column(sa.String(128), nullable=False)
    value = sa.Column(sa.String, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class SmsTemplateModel(DeclarativeBase):

    __tablename__ = "sms_template"
    __table_args__ = {"schema": BASE_SCHEMA}

    sms_template_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column(sa.String(128), nullable=False)
    external_template_id = sa.Column(sa.String(128), nullable=False)
    sms_content = sa.Column(sa.String(10240), nullable=False)
    sms_type = sa.Column(sa.String(32), nullable=False)

    sms_provider_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(f"{BASE_SCHEMA}.sms_provider.sms_provider_id"),
        nullable=False
    )

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class TaxRateModel(DeclarativeBase):

    __tablename__ = "tax_rate"
    __table_args__ = {"schema": BASE_SCHEMA}

    tax_rate_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(512), nullable=True)
    rate = sa.Column(sa.Float, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

