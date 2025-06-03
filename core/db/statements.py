# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
from typing import Optional, List
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy import inspect, String, Text, Unicode, UnicodeText
from sqlalchemy import update, func, desc, and_, or_
from sqlalchemy.future import select
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.models.meta import (
    AdminModel,
    AdminInviteModel,

    RoleModel,
    AdminRoleModel,

    TenantConfigModel,
)

from core.db.models.tenant import (
    PlanModel,
    FeatureModel,
    PlanFeatureModel,

    UserModel,
    AddressModel,
    UserAddressModel,

    PersonModel,
    UserPersonModel,
    PersonIdentityModel,

    CharityModel,
    UserCharityModel,
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


def stmt_delete(model, where: dict, updated_by: int):

    stmt = update(model)

    has_conditions = False
    for field, value in where.items():

        has_conditions = True

        stmt = stmt.where(
            getattr(model, field) == value
        )

    if not has_conditions:
        raise Exception(
            f"Quiting as no filter conditions provoided while deleting all the entries in '{model.__name__}'"
        )

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED
    )

    return stmt


def stmt_query_admin(
        email: Optional[str] = None,
        admin_id: Optional[int] = None,
        admin_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        AdminModel
    ).where(
        AdminModel.is_active == is_active
    )

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


def stmt_delete_admin_roles(where: dict, updated_by: int):

    stmt = update(AdminRoleModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(AdminRoleModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED
    )

    return stmt


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


def stmt_query_plan(
        plan_slug: Optional[StringFilter] = None,
        name: Optional[StringFilter] = None,
        is_listable: Optional[bool] = None,
        category: Optional[StringFilter] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        PlanModel
    ).where(
        PlanModel.is_active == is_active
    )

    if plan_slug:
        stmt = stmt.where(
            prepare_where_expression(
                field=PlanModel.plan_slug,
                operator=plan_slug.operator.value,
                value=plan_slug.value,
                case_insensitive=False,
            )
        )

    if name:
        stmt = stmt.where(
            prepare_where_expression(
                field=PlanModel.name, operator=name.operator.value, value=name.value
            )
        )

    if is_listable is not None:
        stmt = stmt.where(PlanModel.is_listable == is_listable)

    if category:
        stmt = stmt.where(
            prepare_where_expression(
                field=PlanModel.category, operator=category.operator.value, value=category.value
            )
        )

    return stmt


def stmt_delete_plan_feature(where: dict, updated_by: int):

    stmt = update(PlanFeatureModel)

    has_conditions = False
    for field, value in where.items():

        has_conditions = True

        stmt = stmt.where(
            getattr(PlanFeatureModel, field) == value
        )

    if not has_conditions:
        raise Exception(
            f"Quiting as no filter conditions provoided while deleting all the entries in 'PlanFeatureModel'"
        )

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED
    )

    return stmt


def stmt_query_user(
        user_slug: Optional[str] = None,
        phone: Optional[StringFilter] = None,
        email: Optional[StringFilter] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        UserModel
    ).where(
        UserModel.is_active == is_active
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


def stmt_delete_user_address(where: dict, updated_by: int):

    stmt = update(UserAddressModel)

    has_conditions = False
    for field, value in where.items():

        has_conditions = True

        stmt = stmt.where(
            getattr(UserAddressModel, field) == value
        )

    if not has_conditions:
        raise Exception(
            f"Quiting as no filter conditions provoided while deleting all the entries in 'UserAddressModel'"
        )

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED
    )

    return stmt


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


def stmt_delete_person_identity(where: dict, updated_by: int):
    return stmt_delete(model=PersonIdentityModel, where=where, updated_by=updated_by)


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


