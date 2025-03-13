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
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.alembic import (
    #
    # Reusable Table Fields
    model_unique_id,
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


# Define the User model
class UserModel(DeclarativeBase):

    __tablename__ = "user"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    unique_id = model_unique_id()
    name = sa.Column(sa.String(128), nullable=True)
    father_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_nri = sa.Column(sa.Boolean, nullable=True)
    is_active = model_is_active()
    created_date = model_created_date()
    updated_date = model_updated_date()
