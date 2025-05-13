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
from sqlalchemy.dialects import postgresql
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


# Define the Organization Model
class OrganizationModel(DeclarativeBase):

    __tablename__ = "organization"
    __table_args__ = {"schema": BASE_SCHEMA}

    organization_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    organization_slug = model_slug(field_name='organization_slug')
    name = sa.Column(sa.String(256), nullable=False)
    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the User model
class UserModel(DeclarativeBase):

    __tablename__ = "user"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_slug = model_slug(field_name='user_slug')
    name = sa.Column(sa.String(128), nullable=True)
    parent_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_nri = sa.Column(sa.Boolean, nullable=True)
    religion = sa.Column(sa.String(16), nullable=True)

    organization_id = sa.Column(
        sa.BigInteger,
        sa.ForeignKey(f"{BASE_SCHEMA}.organization.organization_id"),
        nullable=True
    )
    is_internal = sa.Column(sa.Boolean, nullable=False, default=False)
    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)
    password_hash = sa.Column(sa.String(256), nullable=True)
    password_hash_algo = sa.Column(sa.String(10240), nullable=True)
    password_expires_after = sa.Column(sa.DateTime, nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()

    # Relationship for easy access
    contacts: Mapped[list["UserContactModel"]] = relationship("UserContactModel", back_populates="user")  # , back_populates="user")


# Define the User model
class UserInviteModel(DeclarativeBase):

    __tablename__ = "user_invite"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_invite_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_invite_slug = model_slug(field_name='user_invite_slug')
    token = sa.Column(sa.String(10240), nullable=False)
    email = sa.Column(sa.String(256), nullable=False)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    roles = sa.Column(postgresql.ARRAY(sa.String), nullable=False)
    status = sa.Column(sa.String(64), nullable=False)
    expires_after = sa.Column(sa.DateTime, nullable=False)

    invited_by = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Role model
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

    # plan_features: Mapped[list["PlanFeatureModel"]] = relationship(
    #     "PlanFeatureModel",
    #     primaryjoin=(
    #     "   and_("
    #     "       PlanModel.plan_id == PlanFeatureModel.plan_id, "
    #     "       PlanFeatureModel.is_active == 'Y'"
    #     "   )"
    #     ),
    #     lazy='select'
    # )


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

    # features: Mapped[list["FeatureModel"]] = relationship(
    #     "FeatureModel",
    #     primaryjoin=(
    #     "   and_("
    #     "       PlanFeatureModel.feature_id == FeatureModel.feature_id, "
    #     "       FeatureModel.is_active == 'Y'"
    #     "   )"
    #     ),
    #     lazy='select'
    # )


# Define the Coupon model
class CouponModel(DeclarativeBase):

    __tablename__ = "coupon"
    __table_args__ = {"schema": BASE_SCHEMA}

    coupon_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    coupon_slug = model_slug(field_name='coupon_slug')
    code = sa.Column(sa.String(64), nullable=False)
    discount_type = sa.Column(sa.String(64), nullable=False)
    discount = sa.Column(sa.Integer, nullable=False)
    min_order = sa.Column(sa.Numeric(10, 2), nullable=True)
    start_date = sa.Column(sa.DateTime(timezone=False), nullable=False)
    end_date = sa.Column(sa.DateTime(timezone=False), nullable=False)
    is_expired = sa.Column(sa.Boolean, nullable=False, default=False)

    # Usage limits
    max_uses = sa.Column(sa.Integer, nullable=True)
    used_count = sa.Column(sa.Integer, nullable=False, default=0)

    # Restriction configuration
    restriction_type = sa.Column(sa.String(64), nullable=True)
    restriction_value = sa.Column(sa.Integer, nullable=False, default=0)

    # User targeting
    for_new_users_only = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the CouponPlan model
class CouponPlanModel(DeclarativeBase):

    __tablename__ = "coupon_plan"
    __table_args__ = {"schema": BASE_SCHEMA}

    coupon_plan_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    coupon_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.coupon.coupon_id'), nullable=False)
    plan_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.plan.plan_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the POC model
class POCModel(DeclarativeBase):

    __tablename__ = "poc"
    __table_args__ = {"schema": BASE_SCHEMA}

    poc_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    poc_slug = model_slug(field_name='poc_slug')
    name = sa.Column(sa.String(128), nullable=False)
    phone = sa.Column(sa.String(32), nullable=True)
    email = sa.Column(sa.String(128), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the ImmovableAsset model
class ImmovableAssetModel(DeclarativeBase):

    __tablename__ = "immovable_asset"
    __table_args__ = {"schema": BASE_SCHEMA}

    immovable_asset_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    immovable_asset_slug = model_slug(field_name='immovable_asset_slug')
    asset_type = sa.Column(sa.String(128), nullable=False)
    asset_sub_type = sa.Column(sa.String(128), nullable=True)
    survey_number = sa.Column(sa.String(128), nullable=True)
    khatha_number = sa.Column(sa.String(128), nullable=True)
    area = sa.Column(sa.String(128), nullable=True)
    holding_type = sa.Column(sa.String(128), nullable=False)
    value = sa.Column(sa.BigInteger, nullable=True)
    notes = sa.Column(sa.String(10240), nullable=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)
    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.address.address_id'), nullable=False)
    poc_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.poc.poc_id'), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


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
    address_slug = model_slug(field_name='address_slug')
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


# Define the Print_request model
class PrintRequestModel(DeclarativeBase):

    __tablename__= "print_request"
    __table_args__= {"schema": BASE_SCHEMA}
    
    print_request_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    print_request_slug = model_slug(field_name='print_request_slug')
    name = sa.Column(sa.String(128), nullable=False)
    phone = sa.Column(sa.String(128), nullable=False)
    email = sa.Column(sa.String(128), nullable=True)
    is_address_exist = sa.Column(sa.Boolean, nullable=True)
    address_id = sa.Column(sa.BigInteger, nullable=True)
    status = sa.Column(sa.String(32), nullable=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    will_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.will.will_id"), nullable=False)

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
    parent_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_nri = sa.Column(sa.Boolean, nullable=True)
    religion = sa.Column(sa.String(16), nullable=True)

    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)

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
    id_type = sa.Column(sa.String(64), nullable=False)
    id_value = sa.Column(sa.String(64), nullable=False)

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
    point_of_contact = sa.Column(sa.String(128), nullable=True)
    phone = sa.Column(sa.String(128), nullable=True)
    email = sa.Column(sa.String(128), nullable=True)
    website = sa.Column(sa.String(128), nullable=True)
    notes = sa.Column(sa.String(10240), nullable=True)
    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the UserCharity model
class UserCharityModel(DeclarativeBase):

    __tablename__ = "user_charity"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_charity_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    charity_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.charity.charity_id"), nullable=False)

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
class UserPeopleModel(DeclarativeBase):

    __tablename__ = "user_people"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_people_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    people_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.people.people_id"), nullable=False)
    relation = sa.Column(sa.String(64), nullable=False)
    association = sa.Column(sa.String(64), nullable=False)

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


# Define the WillExecutor model
class WillExecutorModel(DeclarativeBase):

    __tablename__ = "will_executor"
    __table_args__ = {"schema": BASE_SCHEMA}

    will_executor_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    people_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.people.people_id"), nullable=False)
    will_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.will.will_id"), nullable=False)
    executor_type = sa.Column(sa.String(64), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


