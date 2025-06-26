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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.config import (
    BASE_SCHEMA,
    LOG_SCHEMA,
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


# Define the Tariff model
class TariffModel(DeclarativeBase):

    __tablename__ = "tariff"
    __table_args__ = {"schema": BASE_SCHEMA}

    tariff_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tariff_slug = model_slug(field_name='tariff_slug')

    category = sa.Column(sa.String(32), nullable=False)
    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1204), nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    is_listable = sa.Column(sa.Boolean, nullable=True, default=True)
    is_recommended = sa.Column(sa.Boolean, nullable=True, default=False)
    duration_unit = sa.Column(sa.String(32), nullable=False)
    duration_value = sa.Column(sa.Integer, nullable=False)

    covered_tariff_id = sa.Column(postgresql.ARRAY(sa.Integer), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


# Define the Tariff_Feature model
class TariffFeatureModel(DeclarativeBase):

    __tablename__ = "tariff_feature"
    __table_args__ = {"schema": BASE_SCHEMA}

    tariff_feature_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tariff_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.tariff.tariff_id"), nullable=False)
    feature_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.feature.feature_id"), nullable=False)
    credit = sa.Column(sa.Integer, nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class UserModel(DeclarativeBase):

    __tablename__ = "user"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    user_slug = model_slug(field_name='user_slug')

    name = sa.Column(sa.String(128), nullable=False)
    phone = sa.Column(sa.String(128), nullable=False)
    whatsapp_consent = sa.Column(sa.Boolean, nullable=False, default=True)
    email = sa.Column(sa.String(128), nullable=True)
    parent_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=True)
    gender = sa.Column(sa.String(16), nullable=True)
    is_indian = sa.Column(sa.Boolean, nullable=True)
    religion = sa.Column(sa.String(16), nullable=True)

    is_verified = sa.Column(sa.Boolean, nullable=False, default=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


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


class UserAddressModel(DeclarativeBase):

    __tablename__ = "user_address"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_address_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)
    entity_type = sa.Column(sa.String(32), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class PersonModel(DeclarativeBase):

    __tablename__ = "person"
    __table_args__ = {"schema": BASE_SCHEMA}

    person_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    person_slug = model_slug(field_name='person_slug')

    name = sa.Column(sa.String(128), nullable=False)
    phone = sa.Column(sa.String(128), nullable=False)
    email = sa.Column(sa.String(128), nullable=True)
    parent_name = sa.Column(sa.String(128), nullable=True)
    dob = sa.Column(sa.Date, nullable=False)
    gender = sa.Column(sa.String(16), nullable=False)

    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=False)
    notes = sa.Column(sa.String(10240), nullable=True)

    photo_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.file.file_id'), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class PersonIdentityModel(DeclarativeBase):

    __tablename__ = "person_identity"
    __table_args__ = {"schema": BASE_SCHEMA}

    person_identity_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    person_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.person.person_id"), nullable=False)
    id_type = sa.Column(sa.String(128), nullable=False)
    id_value = sa.Column(sa.String(128), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class UserPersonModel(DeclarativeBase):

    __tablename__ = "user_person"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_person_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.user.user_id"), nullable=False)
    person_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.person.person_id"), nullable=False)

    relation = sa.Column(sa.String(64), nullable=False)
    association = sa.Column(sa.String(64), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


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

    address_id = sa.Column(sa.BigInteger, sa.ForeignKey(f"{BASE_SCHEMA}.address.address_id"), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


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


class CouponTariffModel(DeclarativeBase):

    __tablename__ = "coupon_tariff"
    __table_args__ = {"schema": BASE_SCHEMA}

    coupon_tariff_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    coupon_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.coupon.coupon_id'), nullable=False)
    tariff_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.tariff.tariff_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class TagModel(DeclarativeBase):

    __tablename__ = "tag"
    __table_args__ = {"schema": BASE_SCHEMA}

    tag_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    tag_slug = model_slug(field_name='tag_slug')

    name = sa.Column(sa.String(128), nullable=False)
    description = sa.Column(sa.String(1024), nullable=True)
    category = sa.Column(sa.String(64), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class TariffTagModel(DeclarativeBase):

    __tablename__ = "tariff_tag"
    __table_args__ = {"schema": BASE_SCHEMA}

    tariff_tag_id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    tariff_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.tariff.tariff_id'), nullable=False)
    tag_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.tag.tag_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class CartModel(DeclarativeBase):

    __tablename__ = "cart"
    __table_args__ = {"schema": BASE_SCHEMA}

    cart_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cart_slug = model_slug(field_name='cart_slug')
    user_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)
    coupon_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.coupon.coupon_id'), nullable=True)
    cart_summary = sa.Column(postgresql.JSON(), nullable=False, default=dict)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class CartItemModel(DeclarativeBase):

    __tablename__ = "cart_item"
    __table_args__ = {"schema": BASE_SCHEMA}

    cart_item_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    cart_item_slug = model_slug(field_name='cart_item_slug')

    cart_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.cart.cart_id'), nullable=False)
    tariff_id = sa.Column(sa.Integer, sa.ForeignKey(f'{BASE_SCHEMA}.tariff.tariff_id'), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False, default=1)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class FileModel(DeclarativeBase):

    __tablename__ = "file"
    __table_args__ = {"schema": BASE_SCHEMA}

    file_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    file_slug = model_slug(field_name='file_slug')

    file_name = sa.Column(sa.String(128), nullable=False)
    category = sa.Column(sa.String(128), nullable=False)
    content_type = sa.Column(sa.String(128), nullable=False)
    file_size = sa.Column(sa.BigInteger, nullable=False)

    storage_provider = sa.Column(sa.String(128), nullable=False)
    path = sa.Column(sa.String(10240), nullable=False)
    thumbnail_path = sa.Column(sa.String(10240), nullable=True)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class SmsLogModel(DeclarativeBase):

    __tablename__ = "sms_log"
    __table_args__ = {"schema": BASE_SCHEMA}

    sms_log_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)

    sms_provider_id = sa.Column(sa.Integer, nullable=False)

    reference_id = sa.Column(sa.String(256), nullable=False)
    status = sa.Column(sa.String(16), nullable=False)
    initial_response = sa.Column(postgresql.JSON(), nullable=False, default=dict)
    query_response = sa.Column(postgresql.JSON(), nullable=False, default=dict)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class ApiLogModel(DeclarativeBase):

    __tablename__ = "api_log"
    __table_args__ = {"schema": LOG_SCHEMA}

    api_log_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=True)
    request_id = sa.Column(UUID(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()"))

    method = sa.Column(sa.String(16), nullable=False)
    path = sa.Column(sa.String(512), nullable=False)
    client = sa.Column(sa.String(1024), nullable=False)
    server = sa.Column(sa.String(128), nullable=False)
    api_name = sa.Column(sa.String(128), nullable=False)
    status = sa.Column(sa.String(16), nullable=False)
    status_code = sa.Column(sa.Integer, nullable=False)
    error_detail = sa.Column(sa.String(10240), nullable=True)
    error_trace = sa.Column(sa.String, nullable=True)

    created_date = model_created_date()
    updated_date = model_updated_date()


class PaymentModel(DeclarativeBase):

    __tablename__ = "payment"
    __table_args__ = {"schema": BASE_SCHEMA}

    payment_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    payment_slug = model_slug(field_name='payment_slug')

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)
    cart_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.cart.cart_id'), nullable=False)
    razorpay_order_id = sa.Column(sa.String(128), nullable=True)
    razorpay_payment_id = sa.Column(sa.String(128), nullable=True)
    amount = sa.Column(sa.Float, nullable=False)
    event = sa.Column(sa.String(128), nullable=True)
    request = sa.Column(postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::json"))
    response = sa.Column(postgresql.JSON(), nullable=False, server_default=sa.text("'{}'::json"))
    is_verified = sa.Column(sa.Boolean, nullable=False, server_default=sa.text('FALSE'))

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()



class UserTariffModel(DeclarativeBase):

    __tablename__ = "user_tariff"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_tariff_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)

    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)
    tariff_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.tariff.tariff_id'), nullable=False)
    quantity = sa.Column(sa.Integer, nullable=False, default=1)
    payment_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.payment.payment_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class WillModel(DeclarativeBase):

    __tablename__ = "will"
    __table_args__ = {"schema": BASE_SCHEMA}

    will_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    will_slug = model_slug(field_name='will_slug')
    name = sa.Column(sa.String(128), nullable=True)
    description = sa.Column(sa.String(1024), nullable=True)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class UserWillModel(DeclarativeBase):

    __tablename__ = "user_will"
    __table_args__ = {"schema": BASE_SCHEMA}

    user_will_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    user_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.user.user_id'), nullable=False)
    will_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.will.will_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()


class WillWitnessModel(DeclarativeBase):

    __tablename__ = "will_witness"
    __table_args__ = {"schema": BASE_SCHEMA}

    will_witness_id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    will_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.will.will_id'), nullable=False)
    person_id = sa.Column(sa.BigInteger, sa.ForeignKey(f'{BASE_SCHEMA}.person.person_id'), nullable=False)

    is_active = model_is_active()
    updated_by = model_updated_by()
    created_date = model_created_date()
    updated_date = model_updated_date()
