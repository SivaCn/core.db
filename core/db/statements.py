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


