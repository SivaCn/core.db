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
from sqlalchemy.ext.hybrid import hybrid_property
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
    religion = sa.Column(sa.String(16), nullable=True)
    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

    # Relationship for easy access
    contacts: Mapped[list["UserContactModel"]] = relationship("UserContactModel", back_populates="user")  # , back_populates="user")


# Define the Role model
class RoleModel(DeclarativeBase):

    __tablename__ = "role"
    __table_args__ = {"schema": BASE_SCHEMA}

    role_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String(128), nullable=False)
    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the User_Role model
class UserRoleModel(DeclarativeBase):

    __tablename__ = "user_role"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_role_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    role_id = sa.Column(sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.role.role_id"), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Feature model
class FeatureModel(DeclarativeBase):

    __tablename__ = "feature"
    __table_args__ = {"schema": BASE_SCHEMA}

    feature_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
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
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1204), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    is_listable = sa.Column(sa.Boolean, nullable=True, default=True)
    is_recommended = sa.Column(sa.Boolean, nullable=True, default=False)
    duration_unit = sa.Column(sa.String(32), nullable=False)
    duration_value = sa.Column(sa.Integer, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

    plan_features: Mapped[list["PlanFeatureModel"]] = relationship(
        "PlanFeatureModel",
        primaryjoin=(
        "   and_("
        "       PlanModel.plan_id == PlanFeatureModel.plan_id, "
        "       PlanFeatureModel.is_active == 'Y'"
        "   )"
        ),
        lazy='select'
    )


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

    features: Mapped[list["FeatureModel"]] = relationship(
        "FeatureModel",
        primaryjoin=(
        "   and_("
        "       PlanFeatureModel.feature_id == FeatureModel.feature_id, "
        "       FeatureModel.is_active == 'Y'"
        "   )"
        ),
        lazy='select'
    )


# Define the purchase model
class PurchaseModel(DeclarativeBase):

    __tablename__ = "purchase"
    __table_args__ = {"schema": BASE_SCHEMA}

    purchase_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    plan_feature_id = sa.Column(
        sa.Integer, sa.ForeignKey(f"{BASE_SCHEMA}.plan_feature.plan_feature_id"), nullable=False
    )
    purchase_date = sa.Column(sa.DateTime, nullable=False)
    expiry_date = sa.Column(sa.DateTime, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the UserContact model
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
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

    # Relationship for easy access
    # user = relationship("UserModel")  # , back_populates="user")
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="contacts")  # , back_populates="user")


# Define the Address model
class AddressModel(DeclarativeBase):

    __tablename__ = "address"
    __table_args__ = {"schema": BASE_SCHEMA}

    address_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    line1 = sa.Column(sa.String(512), nullable=False)
    line2 = sa.Column(sa.String(512), nullable=True)
    city = sa.Column(sa.String(64), nullable=False)
    state = sa.Column(sa.String(64), nullable=False)
    country = sa.Column(sa.String(64), nullable=False)
    postal_code = sa.Column(sa.Integer, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the People model
class PeopleModel(DeclarativeBase):

    __tablename__ = "people"
    __table_args__ = {"schema": BASE_SCHEMA}

    people_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    people_slug = model_slug(field_name='people_slug')
    name = sa.Column(sa.String(128), nullable=True)
    father_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_nri = sa.Column(sa.Boolean, nullable=True)
    religion = sa.Column(sa.String(16), nullable=True)
    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the PeopleAddress model
class PeopleAddressModel(DeclarativeBase):

    __tablename__ = "people_address"
    __table_args__ = {"schema": BASE_SCHEMA}

    people_address_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    people_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.people.people_id"), nullable=False)
    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)
    is_default = sa.Column(sa.Boolean, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the PeopleIdentity model
class PeopleIdentityModel(DeclarativeBase):

    __tablename__ = "people_identity"
    __table_args__ = {"schema": BASE_SCHEMA}

    people_identity_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    people_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.people.people_id"), nullable=False)
    type = sa.Column(sa.String(64), nullable=False)
    value = sa.Column(sa.String(64), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Charity model
class CharityModel(DeclarativeBase):

    __tablename__ = "charity"
    __table_args__ = {"schema": BASE_SCHEMA}

    charity_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    charity_slug = model_slug(field_name='charity_slug')
    name = sa.Column(sa.String(128), nullable=False)
    contact_person = sa.Column(sa.String(128), nullable=True)
    phone = sa.Column(sa.String(128), nullable=True)
    email = sa.Column(sa.String(128), nullable=True)
    website = sa.Column(sa.String(128), nullable=True)
    notes = sa.Column(sa.String(10240), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the UserAddress model
class UserAddressModel(DeclarativeBase):

    __tablename__ = "user_address"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_address_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)
    is_default = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the UserPeople model
class userPeopleModel(DeclarativeBase):

    __tablename__ = "user_people"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_people_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    people_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.people.people_id"), nullable=False)
    bond = sa.Column(sa.String(64), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Will model
class WillModel(DeclarativeBase):

    __tablename__ = "will"
    __table_args__ = {"schema": BASE_SCHEMA}

    will_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    will_slug = model_slug(field_name='will_slug')
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    is_generated = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the WillProgress model
class WillProgressModel(DeclarativeBase):

    __tablename__ = "will_progress"
    __table_args__ = {"schema": BASE_SCHEMA}

    will_progress_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    will_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.will.will_id"), nullable=False)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    current_stage = sa.Column(sa.String(128), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


