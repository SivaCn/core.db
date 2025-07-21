# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
from datetime import date
from typing import Optional, List
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy import (
    inspect,
    String,
    Text,
    Unicode,
    UnicodeText,
    literal,
    update,
    func,
    desc,
    and_,
    or_,
)
from sqlalchemy.future import select
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.models.meta import (
    AdminModel,
    AdminInviteModel,

    RoleModel,
    AdminRoleModel,

    TenantConfigModel,

    SmsProviderModel,
    SmsProviderConfigModel,
    SmsTemplateModel,

    TaxRateModel,
)

from core.db.models.tenant import (
    UserModel,
    AddressModel,
    UserAddressModel,

    TagModel,

    TariffModel,
    FeatureModel,
    TariffTagModel,
    TariffFeatureModel,

    CartModel,
    CartItemModel,

    PersonModel,
    UserPersonModel,
    PersonIdentityModel,

    CharityModel,
    UserCharityModel,

    CouponModel,
    CouponTariffModel,

    FileModel,

    PaymentModel,

    WillModel,
    WillStageModel,
    WillWitnessModel,
    UserWillModel,

    UserSessionModel,

    WillExecutorModel,
    PrintRequestModel,

    WillGuardianModel,

    UserTariffModel,
    WillGuardianDependentModel,

    PriceChartModel,
    PriceChartDetailModel,
)

from core.utils.constants import (
    const_business,
    const_operators,
)

from core.utils.helpers.utils import (
    DotDict,
)

from core.utils.helpers.date import (
    utc_now,
)

from web.backend.common import (
    PageArgs,
    PagedType,

    StringFilter,
    NumericFilter,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


def page_meta(count: int, items_per_page: int, current_page: int) -> dict:

    total_pages = (count + items_per_page - 1) // items_per_page

    return {
        'is_first_page': current_page == 1,
        'is_last_page': current_page == total_pages,
        'has_previous_page': current_page > 1,
        'has_next_page': current_page < total_pages,
        'total_items': count,
        'total_pages': total_pages,
        'items_per_page': items_per_page,
        'current_page': current_page
    }


async def paginate(session, stmt, page_args: Optional[PageArgs] = None):

    if page_args and page_args.items_per_page:
        items_per_page = page_args.items_per_page
    else:
        items_per_page = const_business.DEFAULT_ITEMS_PER_PAGE

    if page_args and page_args.current_page:
        current_page = page_args.current_page
    else:
        current_page = const_business.DEFAULT_CURRENT_PAGE

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_cursor = await session.execute(count_stmt)
    count = count_cursor.scalars().one_or_none() or 0

    offset = items_per_page * (current_page - 1)

    data_stmt = stmt.limit(items_per_page).offset(offset)

    paginated = PagedType(
        **page_meta(count=count, items_per_page=items_per_page, current_page=current_page)
    )

    return paginated, data_stmt


def prepare_where_expression(field, operator, value, case_insensitive=True):
    """Custom where clause expression builder.

    Usage:
        >>> prepare_where_expression(field=CouponModel.discount, operator='=', value=100)
        <sqlalchemy.sql.elements.BinaryExpression object at 0x795f1e774350>
        >>>
        >>> str(prepare_where_expression(field=CouponModel.discount, operator='=', value=100))
        'base_schema.coupon.discount = :discount_1'
    """

    operator_func = {
        const_operators.EQUAL: '__eq__',
        const_operators.NOT_EQUAL: '__ne__',
        const_operators.LESS_THAN: '__lt__',
        const_operators.LESS_THAN_OR_EQUAL: '__le__',
        const_operators.GREATER_THAN: '__gt__',
        const_operators.GREATER_THAN_OR_EQUAL: '__ge__',

        const_operators.ANY: 'in_',
        const_operators.NOT_ANY: 'not_in',

        const_operators.CONTAINS: 'icontains',
    }.get(operator)

    if not operator_func:
        raise Exception(f"Operator: '{operator}', is not supported")

    if case_insensitive:
        if isinstance(field.type, (String, Text, Unicode, UnicodeText, )):
            #
            # Make Case-insensitive searches for String Fields.
            if operator in (const_operators.EQUAL, ):
                operator_func = 'ilike'
            if operator in (const_operators.NOT_EQUAL, ):
                operator_func = 'notilike'

    func = getattr(field, operator_func, None)
    if not func:
        raise Exception(
            f"Attribute: '{field.name}', from Model: {field.class_.__name__}, does not support '{operator}'"
        )

    return func(value)


def stmt_delete(model, where: dict, updates: Optional[dict] = None):

    stmt = update(model)

    has_conditions = False
    for field, value in where.items():

        field_obj = getattr(model, field)

        if isinstance(value, (list, tuple)):
            operator, *attrs = value

            if operator == 'not equal to':
                stmt = stmt.where(field_obj != attrs[0])

            if operator == 'in':
                stmt = stmt.where(field_obj.in_(attrs))

            if operator == 'not in':
                stmt = stmt.where(~field_obj.in_(attrs))

            if operator == 'greater than':
                stmt = stmt.where(field_obj < attrs[0])

            if operator == 'lesser than':
                stmt = stmt.where(field_obj > attrs[0])

        else:
            #
            # Applies Equal to condition
            stmt = stmt.where(field_obj == value)

        has_conditions = True

    if not has_conditions:
        raise Exception(
            f"Quiting as no filter conditions provoided while deleting all the entries in '{model.__name__}'"
        )

    #
    # Build susbtitute values
    stmt = stmt.values(
        is_active=const_business.IS_ACTIVE_DELETED,
        **{key: value for key, value in (updates or dict()).items()}
    )

    return stmt


def stmt_query_admin(
        email: Optional[str] = None,
        admin_id: Optional[int] = None,
        admin_slug: Optional[str] = None):
        # is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        AdminModel
    )
    # ).where(
    #     AdminModel.is_active == is_active
    # )

    if email:
        stmt = stmt.where(AdminModel.email == email)

    if admin_id:
        stmt = stmt.where(AdminModel.admin_id == admin_id)

    if admin_slug:
        stmt = stmt.where(AdminModel.admin_slug == admin_slug)

    return stmt


def stmt_query_admin_invite(
        admin_id: Optional[int] = None,
        admin_invite_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        AdminInviteModel
    ).where(
        AdminInviteModel.is_active == is_active
    )

    if admin_id:
        stmt = stmt.where(AdminInviteModel.admin_id == admin_id)

    if admin_invite_slug:
        stmt = stmt.where(AdminInviteModel.admin_invite_slug == admin_invite_slug)

    return stmt


def stmt_refresh_user_invite():

    return update(
        AdminInviteModel
    ).where(
        and_(
            AdminInviteModel.expires_after <= utc_now(),
            AdminInviteModel.status.in_([const_business.INVITED, const_business.RE_INVITED]),
        )
    ).values(
        status=const_business.EXPIRED
    )


def stmt_query_roles(
        name: Optional[StringFilter] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        RoleModel
    ).where(
        RoleModel.is_active == is_active
    )

    if name:
        stmt = stmt.where(
            prepare_where_expression(
                field=RoleModel.name, operator=name.operator.value, value=name.value
            )
        )

    return stmt


def stmt_query_roles_by_admin(
        admin_id: Optional[int] = None,
        admin_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        RoleModel
    ).join(
        AdminRoleModel,
        and_(
            RoleModel.role_id == AdminRoleModel.role_id,
            AdminRoleModel.is_active == const_business.IS_ACTIVE_YES
        )
    ).where(
        RoleModel.is_active == is_active
    )

    if admin_id:
        stmt = stmt.where(AdminRoleModel.admin_id == admin_id)

    if admin_slug:
        stmt = stmt.where(AdminRoleModel.admin_slug == admin_slug)

    return stmt


def stmt_delete_admin_roles(where: dict, updates: dict):
    return stmt_delete(model=AdminRoleModel, where=where, updates=updates)


def stmt_query_tenant_config(
        tenant_config_id: Optional[int] = None,
        tenant_config_slug: Optional[str] = None,
        workspace: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        TenantConfigModel
    ).where(
        TenantConfigModel.is_active == is_active
    )

    if tenant_config_id:
        stmt = stmt.where(
            TenantConfigModel.tenant_config_id == tenant_config_id
        )

    if tenant_config_slug:
        stmt = stmt.where(
            TenantConfigModel.tenant_config_slug == tenant_config_slug
        )

    if workspace:
        stmt = stmt.where(
            TenantConfigModel.workspace == workspace
        )

    stmt = stmt.order_by(
        TenantConfigModel.tenant_config_id
    )

    return stmt


def stmt_query_feature(
        name_list: Optional[List[str]] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        FeatureModel
    ).where(
        FeatureModel.is_active == is_active
    )

    if name_list:
        stmt = stmt.where(
            FeatureModel.name.in_(name_list)
        )

    return stmt


def stmt_query_tariff(
        tariff_id: Optional[NumericFilter] = None,
        tariff_slug: Optional[StringFilter] = None,
        name: Optional[StringFilter] = None,
        is_listable: Optional[bool] = None,
        category: Optional[StringFilter] = None,
        covered_tariff_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        TariffModel
    ).where(
        TariffModel.is_active == is_active
    )

    if tariff_id:
        stmt = stmt.where(
            prepare_where_expression(
                field=TariffModel.tariff_id,
                operator=tariff_id.operator.value,
                value=tariff_id.value
            )
        )

    if tariff_slug:
        stmt = stmt.where(
            prepare_where_expression(
                field=TariffModel.tariff_slug,
                operator=tariff_slug.operator.value,
                value=tariff_slug.value,
                case_insensitive=False,
            )
        )

    if name:
        stmt = stmt.where(
            prepare_where_expression(
                field=TariffModel.name, operator=name.operator.value, value=name.value
            )
        )

    if is_listable is not None:
        stmt = stmt.where(TariffModel.is_listable == is_listable)

    if category:
        stmt = stmt.where(
            prepare_where_expression(
                field=TariffModel.category, operator=category.operator.value, value=category.value
            )
        )

    if covered_tariff_id:
        stmt = stmt.where(
            TariffModel.covered_tariff_id.any(covered_tariff_id)
        )

    return stmt


def stmt_list_user_active_tariffs(user_id: int):

    return select(
        TariffModel
    ).join(
        UserTariffModel,
        and_(
            UserTariffModel.tariff_id == TariffModel.tariff_id,
            UserTariffModel.is_active == const_business.IS_ACTIVE_YES,
        )
    ).where(
        UserTariffModel.user_id == user_id,
        TariffModel.is_active == const_business.IS_ACTIVE_YES,
    )


def stmt_delete_tariff_feature(where: dict, updates: dict):
    return stmt_delete(model=TariffFeatureModel, where=where, updates=updates)


def stmt_query_user(
        user_id: Optional[int] = None,
        user_slug: Optional[str] = None,
        phone: Optional[StringFilter] = None,
        email: Optional[StringFilter] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserModel
    ).where(
        UserModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(
            UserModel.user_id == user_id
        )

    if user_slug:
        stmt = stmt.where(
            UserModel.user_slug == user_slug
        )

    if phone:
        stmt = stmt.where(
            prepare_where_expression(
                field=UserModel.phone,
                operator=phone.operator.value,
                value=phone.value,
            )
        )

    if email:
        stmt = stmt.where(
            prepare_where_expression(
                field=UserModel.email,
                operator=email.operator.value,
                value=email.value,
            )
        )

    return stmt


def stmt_query_address(
        address_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        AddressModel
    ).where(
        AddressModel.is_active == is_active
    )

    if address_id:
        stmt = stmt.where(
            AddressModel.address_id == address_id
        )

    return stmt


def stmt_query_user_address(
        user_id: Optional[int] = None,
        address_id: Optional[int] = None,
        entity_type: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserAddressModel
    ).where(
        UserAddressModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(
            UserAddressModel.user_id == user_id
        )

    if address_id:
        stmt = stmt.where(
            UserAddressModel.address_id == address_id
        )

    if entity_type:
        stmt = stmt.where(
            UserAddressModel.entity_type == entity_type
        )

    return stmt


def stmt_query_address_by_user(
        user_id: int,
        entity_type: Optional[str] = None):

    stmt = select(
        AddressModel
    ).join(
        UserAddressModel,
        and_(
            UserAddressModel.address_id == AddressModel.address_id,
            UserAddressModel.is_active == const_business.IS_ACTIVE_YES,
        )
    ).where(
        UserAddressModel.user_id == user_id
    )

    if entity_type:
        stmt = stmt.where(
            UserAddressModel.entity_type == entity_type
        )

    return stmt


def stmt_delete_user_address(where: dict, updates: dict):
    return stmt_delete(model=UserAddressModel, where=where, updates=updates)


def stmt_query_person(
        person_id: Optional[int] = None,
        person_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        PersonModel
    ).where(
        PersonModel.is_active == is_active
    )

    if person_id:
        stmt = stmt.where(
            PersonModel.person_id == person_id
        )

    if person_slug:
        stmt = stmt.where(
            PersonModel.person_slug == person_slug
        )

    return stmt


def stmt_query_person_identity(
        person_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        PersonIdentityModel
    ).where(
        PersonIdentityModel.is_active == is_active
    )

    if person_id:
        stmt = stmt.where(
            PersonIdentityModel.person_id == person_id
        )

    return stmt


def stmt_delete_person_identity(where: dict, updates: Optional[dict] = None):
    return stmt_delete(model=PersonIdentityModel, where=where, updates=updates or dict())


def stmt_query_user_person(
        user_id: Optional[int] = None,
        person_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserPersonModel
    ).where(
        UserPersonModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(
            UserPersonModel.user_id == user_id
        )

    if person_id:
        stmt = stmt.where(
            UserPersonModel.person_id == person_id
        )

    return stmt


def stmt_query_charity(
        charity_id: Optional[int] = None,
        charity_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        CharityModel
    ).where(
        CharityModel.is_active == is_active
    )

    if charity_id:
        stmt = stmt.where(
            CharityModel.charity_id == charity_id
        )

    if charity_slug:
        stmt = stmt.where(
            CharityModel.charity_slug == charity_slug
        )

    return stmt


def stmt_query_user_charity(
        user_id: Optional[int] = None,
        charity_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserCharityModel
    ).where(
        UserCharityModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(
            UserCharityModel.user_id == user_id
        )

    if charity_id:
        stmt = stmt.where(
            UserCharityModel.charity_id == charity_id
        )

    return stmt


def stmt_query_coupon(
        code: Optional[str] = None,
        coupon_slug: Optional[str] = None,
        coupon_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):


    stmt = select(
        CouponModel
    ).where(
        CouponModel.is_active == is_active
    )

    if coupon_slug:
        stmt = stmt.where(
            CouponModel.coupon_slug == coupon_slug
        )

    if coupon_id:
        stmt = stmt.where(
            CouponModel.coupon_id == coupon_id
        )

    if code:
        stmt = stmt.where(
            CouponModel.code == code
        )

    return stmt


def stmt_delete_coupon_tariff(where: dict, updates: dict):
    return stmt_delete(model=CouponTariffModel, where=where, updates=updates)


def stmt_query_tag(
        name: Optional[str] = None,
        tag_slug: Optional[str] = None,
        tag_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):


    stmt = select(
        TagModel
    ).where(
        TagModel.is_active == is_active
    )

    if name:
        stmt = stmt.where(
            func.lower(TagModel.name) == func.lower(name)
        )

    if tag_slug:
        stmt = stmt.where(
            TagModel.tag_slug == tag_slug
        )

    if tag_id:
        stmt = stmt.where(
            TagModel.tag_id == tag_id
        )

    return stmt


def stmt_delete_tariff_tag(where: dict, updates: dict):
    return stmt_delete(model=TariffTagModel, where=where, updates=updates)


def stmt_query_cart(
        user_id: Optional[str] = None,
        cart_id: Optional[int] = None,
        cart_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        CartModel
    ).where(
        CartModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(
            CartModel.user_id == user_id
        )

    if cart_id:
        stmt = stmt.where(
            CartModel.cart_id == cart_id
        )

    if cart_slug:
        stmt = stmt.where(
            CartModel.cart_slug == cart_slug
        )

    return stmt


def stmt_query_cart_item(
        cart_id: Optional[int] = None,
        tariff_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        CartItemModel
    ).where(
        CartItemModel.is_active == is_active
    )

    if cart_id:
        stmt = stmt.where(
            CartItemModel.cart_id == cart_id
        )

    if tariff_id:
        stmt = stmt.where(
            CartItemModel.tariff_id == tariff_id
        )

    return stmt


def stmt_list_cart_items(
        cart_id: Optional[int] = None,
        cart_slug: Optional[str] = None):

    stmt = select(
        CartModel.cart_slug,
        TariffModel.tariff_slug,
        TariffModel.price,
        CartItemModel.cart_item_slug,
        CartItemModel.quantity,
    ).select_from(
        CartModel
    ).join(
        CartItemModel,
        and_(
            CartItemModel.cart_id == CartModel.cart_id,
            CartItemModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        TariffModel,
        and_(
            TariffModel.tariff_id == CartItemModel.tariff_id,
            TariffModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    )

    if cart_id:
        stmt = stmt.where(
            CartModel.cart_id == cart_id
        )

    if cart_slug:
        stmt = stmt.where(
            CartModel.cart_slug == cart_slug
        )

    return stmt


def stmt_delete_cart(where: dict, updates: dict):
    return stmt_delete(model=CartModel, where=where, updates=updates)


def stmt_delete_cart_item(where: dict, updates: dict):
    return stmt_delete(model=CartItemModel, where=where, updates=updates)


def stmt_query_file(
        file_id: Optional[int] = None,
        file_slug: Optional[str] = None,
        user_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        FileModel
    ).where(
        FileModel.is_active == is_active
    )

    if file_id:
        stmt = stmt.where(
            FileModel.file_id == file_id
        )

    if file_slug:
        stmt = stmt.where(
            FileModel.file_slug == file_slug
        )

    if user_id:
        stmt = stmt.where(
            FileModel.user_id == user_id
        )

    return stmt


def stmt_query_sms_provider(
        name: str,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        SmsProviderModel
    ).where(
        SmsProviderModel.is_active == is_active
    )

    if name:
        stmt = stmt.where(
            SmsProviderModel.name == name
        )

    return stmt


def stmt_query_sms_provider_config(
        sms_provider_id: Optional[int] = None,
        config_type: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        SmsProviderConfigModel
    ).where(
        SmsProviderConfigModel.is_active == is_active
    )

    if sms_provider_id:
        stmt = stmt.where(
            SmsProviderConfigModel.sms_provider_id == sms_provider_id
        )

    if config_type:
        stmt = stmt.where(
            SmsProviderConfigModel.config_type == config_type
        )

    return stmt


def stmt_query_sms_template(
        name: str,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        SmsTemplateModel
    ).where(
        SmsTemplateModel.is_active == is_active
    )

    if name:
        stmt = stmt.where(
            SmsTemplateModel.name == name
        )

    return stmt


def stmt_query_tax_rate(is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    return select(
        TaxRateModel
    ).where(
        TaxRateModel.is_active == is_active,
    ).order_by(
        TaxRateModel.tax_rate_id
    )


def stmt_query_payment(
        payment_id: Optional[int] = None,
        payment_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        PaymentModel
    ).where(
        PaymentModel.is_active == is_active
    )

    if payment_id:
        stmt = stmt.where(
            PaymentModel.payment_id == payment_id
        )

    if payment_slug:
        stmt = stmt.where(
            PaymentModel.payment_slug == payment_slug
        )

    return stmt


def stmt_query_will_stage(
        name: Optional[str] = None,
        priority: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        WillStageModel
    ).where(
        WillStageModel.is_active == is_active,
    )

    if name:
        stmt = stmt.where(
            WillStageModel.name == name
        )

    if priority:
        stmt = stmt.where(
            WillStageModel.priority == priority
        )

    stmt = stmt.order_by(
        WillStageModel.priority
    )

    return stmt


def stmt_query_will(
        will_id: Optional[int] = None,
        will_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        WillModel
    ).where(
        WillModel.is_active == is_active
    )

    if will_id:
        stmt = stmt.where(
            WillModel.will_id == will_id
        )

    if will_slug:
        stmt = stmt.where(
            WillModel.will_slug == will_slug
        )

    return stmt

def stmt_query_will_witness(
        will_id: Optional[int] = None,
        person_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        WillWitnessModel
    ).where(
        WillWitnessModel.is_active == is_active
    )

    if will_id:
        stmt = stmt.where(
            WillWitnessModel.will_id == will_id
        )

    if person_id:
        stmt = stmt.where(
            WillWitnessModel.person_id == person_id
        )

    return stmt


def stmt_delete_will_witness(where: dict, updates: dict):
    return stmt_delete(model=WillWitnessModel, where=where, updates=updates)


def stmt_query_user_will(
        user_id: Optional[int] = None,
        will_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(UserWillModel).where(UserWillModel.is_active == is_active)

    if user_id:
        stmt = stmt.where(UserWillModel.user_id == user_id)

    if will_id:
        stmt = stmt.where(UserWillModel.will_id == will_id)

    return stmt


def stmt_list_person(
        user_id: int,
        person_ids: Optional[List[int]] = None,
        adult_only: Optional[bool] = False):

    stmt = select(
        PersonModel.person_id,
        PersonModel.person_slug,
        PersonModel.name,
        PersonModel.phone,
        PersonModel.email,
        PersonModel.parent_name,
        PersonModel.dob,
        PersonModel.gender,
        PersonModel.notes,

        UserPersonModel.relation,
        UserPersonModel.association,

        PersonIdentityModel.id_type,
        PersonIdentityModel.id_value,

        AddressModel.address_slug,
        AddressModel.line1,
        AddressModel.line2,
        AddressModel.city,
        AddressModel.state,
        AddressModel.country,
        AddressModel.postal_code,
        AddressModel.created_date,
        AddressModel.updated_date
    ).select_from(
        PersonModel
    ).join(
        UserPersonModel,
        and_(
            UserPersonModel.person_id == PersonModel.person_id,
            UserPersonModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        PersonIdentityModel,
        and_(
            PersonModel.person_id == PersonIdentityModel.person_id,
            PersonIdentityModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        AddressModel,
        and_(
            PersonModel.address_id == AddressModel.address_id,
            AddressModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).where(
        UserPersonModel.user_id == user_id
    ).order_by(
        PersonModel.person_id
    )

    if person_ids:
        stmt = stmt.where(
            PersonModel.person_id.in_(person_ids)
        )

    if adult_only:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        stmt = stmt.where(PersonModel.dob <= eighteen_years_ago)

    return stmt


def stmt_query_will_by_user_id(user_id: int):

    return select(
        WillModel
    ).join(
        UserWillModel,
        and_(
            UserWillModel.user_id == user_id,
            UserWillModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    )


def stmt_query_will_executor(
        will_id: Optional[int] = None,
        person_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(WillExecutorModel).where(WillExecutorModel.is_active == is_active)

    if will_id:
        stmt = stmt.where(
            WillExecutorModel.will_id == will_id
        )

    if person_id:
        stmt = stmt.where(
            WillExecutorModel.person_id == person_id
        )

    stmt = stmt.order_by(WillExecutorModel.is_primary)

    return stmt


def stmt_query_user_session(
        user_session_slug: Optional[str] = None,
        user_id: Optional[int] = None,
        device_id: Optional[str] = None,
        token: Optional[str] = None,
        user_agent: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserSessionModel
    ).where(
        UserSessionModel.is_active == is_active
    )

    if user_session_slug:
        stmt = stmt.where(
            UserSessionModel.user_session_slug == user_session_slug
        )

    if user_id:
        stmt = stmt.where(
            UserSessionModel.user_id == user_id
        )

    if device_id:
        stmt = stmt.where(
            UserSessionModel.device_id == device_id
        )

    if token:
        stmt = stmt.where(
            UserSessionModel.token == token
        )

    if user_agent:
        stmt = stmt.where(
            UserSessionModel.user_agent == user_agent
        )

    return stmt


def stmt_delete_user_session(where: dict, updates: dict):
    return stmt_delete(model=UserSessionModel, where=where, updates=updates)


def stmt_query_list_executor(will_id: int):

    return select(
        PersonModel,
        UserPersonModel,
        WillExecutorModel,
    ).select_from(
        PersonModel
    ).join(
        WillExecutorModel,
        and_(
            PersonModel.person_id == WillExecutorModel.person_id,
            WillExecutorModel.is_active == const_business.IS_ACTIVE_YES,
            PersonModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        UserPersonModel,
        and_(
            UserPersonModel.person_id == PersonModel.person_id,
            UserPersonModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).where(
        WillExecutorModel.will_id == will_id
    ).order_by(
        desc(WillExecutorModel.is_primary)
    )


def stmt_query_print_request(
        user_id: Optional[int] = None,
        will_id: Optional[int] = None,
        status: Optional[list[str]] = None,
        print_request_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        PrintRequestModel
    ).where(
        PrintRequestModel.is_active == is_active
    )

    if user_id:
        stmt = stmt.where(PrintRequestModel.user_id == user_id)

    if will_id:
        stmt = stmt.where(PrintRequestModel.will_id == will_id)

    if status:
        stmt = stmt.where(PrintRequestModel.status.in_(status))

    if print_request_slug:
        stmt = stmt.where(PrintRequestModel.print_request_slug == print_request_slug)

    stmt = stmt.order_by(PrintRequestModel.print_request_id)

    return stmt


def stmt_delete_will_executor(where: dict, updates: dict):
    return stmt_delete(model=WillExecutorModel, where=where, updates=updates)


def stmt_query_will_guardian(
        will_id: Optional[int] = None,
        guardian_id: Optional[int] = None,
        will_guardian_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        WillGuardianModel
    ).where(
        WillGuardianModel.is_active == is_active
    )

    if will_id:
        stmt = stmt.where(WillGuardianModel.will_id == will_id)

    if guardian_id:
        stmt = stmt.where(WillGuardianModel.guardian_id == guardian_id)

    if will_guardian_slug:
        stmt = stmt.where(WillGuardianModel.will_guardian_slug == will_guardian_slug)

    return stmt


def stmt_delete_will_guardian(where: dict, updates: Optional[dict] = None):
    return stmt_delete(model=WillGuardianModel, where=where, updates=updates or dict())


def stmt_auto_expire_tariff(where: dict, updates: Optional[dict] = None):
    return stmt_delete(model=UserTariffModel, where=where, updates=updates or dict())


def stmt_query_guardian_dependent(
        will_guardian_id: Optional[int] = None,
        dependent_id: Optional[int] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        WillGuardianDependentModel
    ).where(
        WillGuardianDependentModel.is_active == is_active
    )

    if will_guardian_id:
        stmt = stmt.where(WillGuardianDependentModel.will_guardian_id == will_guardian_id)

    if dependent_id:
        stmt = stmt.where(WillGuardianDependentModel.dependent_id == dependent_id)

    return stmt


def stmt_delete_guardian_dependent(where: dict, updates: Optional[dict] = None):
    return stmt_delete(model=WillGuardianDependentModel, where=where, updates=updates or dict())


def stmt_list_person_minimal(user_id: int, person_id: int):

    return select(
        PersonModel.person_slug,
        PersonModel.name,
        PersonModel.dob,

        UserPersonModel.relation,
        UserPersonModel.association,
    ).select_from(
        PersonModel
    ).join(
        UserPersonModel,
        and_(
            UserPersonModel.user_id == user_id,
            PersonModel.person_id == UserPersonModel.person_id,
            UserPersonModel.is_active == const_business.IS_ACTIVE_YES,
        )
    ).where(
        PersonModel.person_id == person_id
    )


def stmt_list_person_roles(
        will_id: int,
        person_id: int):

    stmt_executor = select(
        literal("executor").label("role")
    ).select_from(
        WillExecutorModel
    ).where(
        WillExecutorModel.is_active == const_business.IS_ACTIVE_YES,
        WillExecutorModel.will_id == will_id,
        WillExecutorModel.person_id == person_id,
    )

    stmt_guardian = select(
        literal("guardian").label("role")
    ).select_from(
        WillGuardianModel
    ).where(
        and_(
            WillGuardianModel.is_active == const_business.IS_ACTIVE_YES,
            WillGuardianModel.will_id == will_id,
            or_(
                WillGuardianModel.guardian_id == person_id,
                WillGuardianModel.backup_guardian_id == person_id,
            )
        )
    )

    stmt_witness = select(
        literal("witness").label("role")
    ).select_from(
        WillWitnessModel
    ).where(
        WillWitnessModel.is_active == const_business.IS_ACTIVE_YES,
        WillWitnessModel.will_id == will_id,
        WillWitnessModel.person_id == person_id,
    )

    return stmt_executor.union_all(stmt_guardian.union_all(stmt_witness))


def stmt_list_tariff(tariff_slug: Optional[str] = None):

    stmt = select(
        TariffModel.tariff_id,
        TariffModel.tariff_slug,
        TariffModel.name,
        TariffModel.description,
        TariffModel.category,
        TariffModel.price,
        TariffModel.price_chart_id,
        TariffModel.is_listable,
        TariffModel.is_recommended,
        TariffModel.duration_unit,
        TariffModel.duration_value,
        TariffModel.updated_by,
        TariffModel.is_active,
        TariffModel.created_date,
        TariffModel.updated_date,
        TagModel.name.label('tag_name'),
        PriceChartModel.price_chart_slug,
        func.json_agg(
            func.json_build_object(
                'name', FeatureModel.name,
                'accessLimit', TariffFeatureModel.credit
            )
        ).label('features')
    ).select_from(
        TariffModel
    ).join(
        TariffFeatureModel,
        and_(
            TariffFeatureModel.tariff_id == TariffModel.tariff_id,
            TariffFeatureModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        FeatureModel,
        and_(
            TariffFeatureModel.feature_id == FeatureModel.feature_id,
            FeatureModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        TariffTagModel,
        and_(
            TariffTagModel.tariff_id == TariffModel.tariff_id,
            TariffTagModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        TagModel,
        and_(
            TagModel.tag_id == TariffTagModel.tag_id,
            TagModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).join(
        PriceChartModel,
        and_(
            TariffModel.price_chart_id == PriceChartModel.price_chart_id,
            PriceChartModel.is_active == const_business.IS_ACTIVE_YES,
        ),
        isouter=True
    ).group_by(
        TariffModel.tariff_id,
        TariffModel.tariff_slug,
        TariffModel.name,
        TariffModel.description,
        TariffModel.category,
        TariffModel.price,
        TariffModel.price_chart_id,
        TariffModel.is_listable,
        TariffModel.is_recommended,
        TariffModel.duration_unit,
        TariffModel.duration_value,
        TariffModel.updated_by,
        TariffModel.is_active,
        TariffModel.created_date,
        TariffModel.updated_date,
        TagModel.name,
        PriceChartModel.price_chart_slug,
    ).where(
        TariffModel.is_active == const_business.IS_ACTIVE_YES
    ).order_by(
        TariffModel.tariff_id
    )

    if tariff_slug:
        stmt = stmt.where(
            TariffModel.tariff_slug == tariff_slug
        )

    return stmt


def stmt_query_price_chart_detail(price_chart_slug: str):

    return select(
        PriceChartDetailModel.age,
        PriceChartDetailModel.price,
        PriceChartDetailModel.nri_price,
    ).select_from(
        PriceChartDetailModel
    ).join(
        PriceChartModel,
        and_(
            PriceChartModel.price_chart_id == PriceChartDetailModel.price_chart_id,
            PriceChartDetailModel.is_active == const_business.IS_ACTIVE_YES,
        )
    ).where(
        PriceChartModel.price_chart_slug == price_chart_slug,
        PriceChartModel.is_active == const_business.IS_ACTIVE_YES,
    ).order_by(
        PriceChartDetailModel.age
    )

