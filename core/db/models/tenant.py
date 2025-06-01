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

from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.alembic import (
    #
    # Reusable Table Fields
    model_slug,
    model_is_active,
    model_updated_by,
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


# Define the Feature model
class FeatureModel(DeclarativeBase):

    __tablename__ = "feature"
    __table_args__ = {"schema": BASE_SCHEMA}

    feature_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    feature_slug = model_slug(field_name='feature_slug')
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1204), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Plan model
class PlanModel(DeclarativeBase):

    __tablename__ = "plan"
    __table_args__ = {"schema": BASE_SCHEMA}

    plan_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    plan_slug = model_slug(field_name='plan_slug')
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1204), nullable=False)
    category = sa.Column(sa.String(16), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    is_listable = sa.Column(sa.Boolean, nullable=True, default=True)
    is_recommended = sa.Column(sa.Boolean, nullable=True, default=False)
    duration_unit = sa.Column(sa.String(32), nullable=False)
    duration_value = sa.Column(sa.Integer, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Plan_Feature model
class PlanFeatureModel(DeclarativeBase):

    __tablename__ = "plan_feature"
    __table_args__ = {"schema": BASE_SCHEMA}

    plan_feature_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    plan_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.plan.plan_id"), nullable=False)
    feature_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.feature.feature_id"), nullable=False)
    access_limit = sa.Column(sa.Integer, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

