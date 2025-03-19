# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import datetime
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import sqlalchemy as sa

from sqlalchemy.inspection import inspect
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.alembic import (
    #
    # Reusable Table Fields
    model_slug,
    model_is_active,
    model_created_date,
    model_updated_date,

    #
    # Constants
    BASE_SCHEMA,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


# Define the base class for SQLAlchemy models
DeclarativeBase = declarative_base()


def model_as_dict(model_instance):
    """Convert an SQLAlchemy model instance to a dictionary (excluding _sa_instance_state)."""

    return {
        column.key: getattr(model_instance, column.key)
        for column in inspect(model_instance).mapper.column_attrs
    }


# Define the User model
class UserModel(DeclarativeBase):

    __tablename__ = "user"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_slug = model_slug(field_name='user_slug')
    name = sa.Column(sa.String(128), nullable=True)
    father_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_nri = sa.Column(sa.Boolean, nullable=True)
    is_active = model_is_active()
    created_date = model_created_date()
    updated_date = model_updated_date()

    # Relationship for easy access
    contacts: Mapped[list["UserContactModel"]] = relationship("UserContactModel", back_populates="user")  # , back_populates="user")


# Define the User model
class UserContactModel(DeclarativeBase):

    __tablename__ = "user_contact"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_contact_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    category = sa.Column(sa.String(16), nullable=False)
    value = sa.Column(sa.String(128), nullable=False)
    is_primary = sa.Column(sa.Boolean, nullable=False, default=False)
    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)
    whatsapp_consent = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    created_date = model_created_date()
    updated_date = model_updated_date()

    # Relationship for easy access
    user = relationship("UserModel")  # , back_populates="user")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="contacts")  # , back_populates="user")

