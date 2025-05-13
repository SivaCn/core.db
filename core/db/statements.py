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
from core.db.models import (
    UserModel,
    UserAddressModel,
    UserContactModel,

    RoleModel,
    UserRoleModel,

    UserInviteModel,

    MenuModel,
    MenuRoleModel,

    PlanModel,
    FeatureModel,
    PlanFeatureModel,

    CouponModel,
    CouponPlanModel,

    POCModel,
    AddressModel,
    ImmovableAssetModel,

    PeopleModel,
    UserPeopleModel,
    PeopleIdentityModel,

    CharityModel,
    UserCharityModel,

    PrintRequestModel,

    WillModel,
)

from core.utils.constants import (
    const_business,
    const_operators,
)

from core.utils.helpers.utils import (
    DotDict,
)

from core.utils.helpers.validators import (
    validate_is_active,
)

from core.utils.helpers.date import (
    utc_now,
)

from web.backend.common import (
    PageArgs,
    PagedType,

    DateFilter,
    StringFilter,
    NumericFilter,
    CouponDiscountTypeEnum,
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


async def paginate(session: DotDict, stmt, page_args: Optional[PageArgs] = None):

    if page_args and page_args.items_per_page:
        items_per_page = page_args.items_per_page
    else:
        items_per_page = const_business.DEFAULT_ITEMS_PER_PAGE

    if page_args and page_args.current_page:
        current_page = page_args.current_page
    else:
        current_page = const_business.DEFAULT_CURRENT_PAGE

    count_stmt = select(func.count()).select_from(stmt.subquery())
    count_cursor = await session.replica.execute(count_stmt)
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


def stmt_query_admin_user(
        user_slug: Optional[str] = None,
        is_active: Optional[str] = None):

    stmt = select(UserModel).where(UserModel.is_internal == True)

    if user_slug:
        stmt = stmt.where(UserModel.user_slug == user_slug)

    if is_active:
        stmt = stmt.where(UserModel.is_active == is_active)

    return stmt


def stmt_delete_user_roles(where: dict):

    stmt = update(UserRoleModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(UserRoleModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(is_active=const_business.IS_ACTIVE_DELETED)

    return stmt


def stmt_query_roles(
        name: Optional[List[str]] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(RoleModel)

    if is_active:
        if not validate_is_active(is_active):
            raise Exception(f"Argument is_active '{is_active}', is not supported")
        stmt = stmt.where(RoleModel.is_active == is_active)

    if name:
        stmt = stmt.where(RoleModel.name.in_(name)) 

    return stmt


def stmt_query_roles_by_user_id(user_id: int):

    return select(
        RoleModel
    ).join(
        UserRoleModel,
        and_(
            UserRoleModel.is_active == const_business.IS_ACTIVE_YES,
            UserRoleModel.role_id == RoleModel.role_id,
        )
    ).where(
        UserRoleModel.is_active == const_business.IS_ACTIVE_YES,
        UserRoleModel.user_id == user_id,
    )


def stmt_query_menu_list(role_id: int, parent_id: Optional[int] = None):
    """

    Usage:
        >>> cursor = await session.replica.execute(stmt_query_menu_list)
        >>> result = cursor.all()
        '''[
            (<core.db.models.MenuModel object at 0x755c71ccad90>, True, True),
            (<core.db.models.MenuModel object at 0x755c71ccae10>, True, True)
        ]'''
    """

    stmt = select(
        MenuModel,
        MenuRoleModel.can_read.label('can_read'),
        MenuRoleModel.can_write.label('can_write'),
    ).join(
        MenuRoleModel,
        and_(
            MenuModel.menu_id == MenuRoleModel.menu_id,

            MenuRoleModel.role_id == role_id,
            MenuRoleModel.is_active == const_business.IS_ACTIVE_YES,

            or_(
                #
                # Include the Menu only when atleast with one Read or Write
                MenuRoleModel.can_read == True, MenuRoleModel.can_write == True
            )
        )
    ).where(
        MenuModel.is_active == const_business.IS_ACTIVE_YES,
    ).order_by(
        MenuModel.priority
    )

    if parent_id:
        # Get the chile Menus
        stmt = stmt.where(MenuModel.parent_id == parent_id)

    else:
        # Get the root Menus
        stmt = stmt.where(MenuModel.parent_id == None)

    return stmt


def stmt_query_feature(is_active: Optional[bool] = None):

    stmt = select(FeatureModel)

    if is_active is None:
        stmt = stmt.where(
            FeatureModel.is_active == const_business.IS_ACTIVE_YES
        )

    if isinstance(is_active, bool):
        _is_active = const_business.IS_ACTIVE_YES if is_active is True else const_business.IS_ACTIVE_NO
        stmt = stmt.where(
            FeatureModel.is_active == _is_active
        )

    return stmt


def stmt_query_features_by_plan(plan_id: int):

    return select(
        FeatureModel
    ).join(
        PlanFeatureModel,
        and_(
            FeatureModel.feature_id == PlanFeatureModel.feature_id,
            PlanFeatureModel.is_active == const_business.IS_ACTIVE_YES,
        )
    ).where(
        PlanFeatureModel.plan_id == plan_id
    ).order_by(
        FeatureModel.feature_id
    )


def stmt_delete_plan_feature(where: dict):

    stmt = update(PlanFeatureModel)

    for field, value in where.items():

        if field == 'is_active':
            value = const_business.IS_ACTIVE_YES if value is True else const_business.IS_ACTIVE_NO

        stmt = stmt.where(
            getattr(PlanFeatureModel, field) == value
        )

    stmt = stmt.values(is_active=const_business.IS_ACTIVE_DELETED)

    return stmt


def stmt_query_plan(
        is_active: Optional[str] = None,
        plan_slug: Optional[StringFilter] = None,
        name: Optional[StringFilter] = None,
        is_listable: Optional[bool] = None,
        category: Optional[StringFilter] = None):

    stmt = select(PlanModel)

    if is_active:
        stmt = stmt.where(PlanModel.is_active == is_active)

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


def stmt_delete_coupon_plan(where: dict):

    stmt = update(CouponPlanModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(CouponPlanModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(is_active=const_business.IS_ACTIVE_DELETED)

    return stmt


def stmt_query_user_invite(
        is_active: Optional[str] = None,
        user_id: Optional[int] = None,
        status: Optional[List[str]] = None,
        email: Optional[str] = None,
        user_invite_slug: Optional[str] = None,
        user_schema: Optional[dict] = None):

    stmt = select(UserInviteModel)

    if is_active:
        stmt = stmt.where(UserInviteModel.is_active == is_active)

    if user_id:
        stmt = stmt.where(UserInviteModel.user_id == user_id)

    if email:
        stmt = stmt.where(UserInviteModel.email == email)

    if status:
        stmt = stmt.where(UserInviteModel.status.in_(status))

    if user_invite_slug:
        stmt = stmt.where(UserInviteModel.user_invite_slug == user_invite_slug)

    if user_schema:
        join_where = [
            UserModel.user_id == UserInviteModel.user_id
        ]

        for field, value in user_schema.items():

            if field == 'is_active':
                value = const_business.IS_ACTIVE_YES if value is True else const_business.IS_ACTIVE_NO

            join_where.append(
                getattr(UserModel, field) == value
            )

        stmt = stmt.join(
            UserModel,
            and_(*join_where)
        )

    stmt = stmt.order_by(
        UserInviteModel.user_id,
        desc(UserInviteModel.user_invite_id)
    )

    return stmt


def stmt_refresh_user_invite():

    return update(
        UserInviteModel
    ).where(
        and_(
            UserInviteModel.expires_after <= utc_now(),
            UserInviteModel.status.in_([const_business.INVITED, const_business.RE_INVITED]),
        )
    ).values(
        status=const_business.EXPIRED,
        updated_date=utc_now()
    )


def stmt_query_user_contact(
        user_id: Optional[int] = None,
        category: Optional[str] = None,
        value: Optional[str] = None,
        is_primary: Optional[bool] = False,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(UserContactModel)

    if is_active:
        if not validate_is_active(is_active):
            raise Exception(f"Argument is_active '{is_active}', is not supported")
        stmt = stmt.where(UserContactModel.is_active == is_active)

    if user_id:
        stmt = stmt.where(UserContactModel.user_id == user_id)

    if category:
        stmt = stmt.where(UserContactModel.category == category)

    if value:
        stmt = stmt.where(UserContactModel.value == value)

    if is_primary:
        stmt = stmt.where(UserContactModel.is_primary == is_primary)

    return stmt


def stmt_query_coupon(
        coupon_slug: Optional[StringFilter] = None,
        code: Optional[StringFilter] = None,
        discount_type: Optional[CouponDiscountTypeEnum] = None,
        discount: Optional[NumericFilter] = None,
        is_active: Optional[str] = None,
        start_date: Optional[DateFilter] = None,
        end_date: Optional[DateFilter] = None,
        is_expired: Optional[bool] = None,
        used_count: Optional[NumericFilter] = None):

    stmt = select(CouponModel)

    if coupon_slug:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.coupon_slug,
                operator=coupon_slug.operator.value,
                value=coupon_slug.value,
                case_insensitive=False,
            )
        )

    if is_active:
        stmt = stmt.where(CouponModel.is_active == is_active)

    if is_expired:
        stmt = stmt.where(CouponModel.is_expired == is_expired)

    if code:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.code, operator=code.operator.value, value=code.value
            )
        )

    if discount_type:
        stmt = stmt.where(CouponModel.discount_type == discount_type)

    if discount:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.discount, operator=discount.operator.value, value=discount.value
            )
        )

    if start_date:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.start_date, operator=start_date.operator.value, value=start_date.value
            )
        )

    if end_date:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.end_date, operator=end_date.operator.value, value=end_date.value
            )
        )

    if used_count:
        stmt = stmt.where(
            prepare_where_expression(
                field=CouponModel.used_count, operator=used_count.operator.value, value=used_count.value
            )
        )

    stmt = stmt.order_by(
        desc(CouponModel.is_active),
        CouponModel.is_expired,
    )

    return stmt


def stmt_query_poc(poc_id: NumericFilter):

    stmt = select(POCModel)

    stmt = stmt.where(
        POCModel.is_active == const_business.IS_ACTIVE_YES,
    )

    stmt = stmt.where(
        prepare_where_expression(
            field=POCModel.poc_id, operator=poc_id.operator.value, value=poc_id.value
        )
    )

    return stmt


def stmt_query_address(address_id: NumericFilter):

    stmt = select(AddressModel)

    stmt = stmt.where(
        AddressModel.is_active == const_business.IS_ACTIVE_YES,
    )

    stmt = stmt.where(
        prepare_where_expression(
            field=AddressModel.address_id, operator=address_id.operator.value, value=address_id.value
        )
    )

    return stmt


def stmt_query_user_address(user_id: int):

   return select(
        AddressModel
    ).join(
        UserAddressModel,
        and_(
            UserAddressModel.is_default == True,
            UserAddressModel.is_active == const_business.IS_ACTIVE_YES,
            UserAddressModel.address_id == AddressModel.address_id,
        )
    ).where(
        UserAddressModel.user_id == user_id,
    )


def stmt_delete_address(where: dict, updated_by: int):

    stmt = update(AddressModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(AddressModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED
    )

    return stmt


def stmt_delete_user_address(where: dict):

    stmt = update(UserAddressModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(UserAddressModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(is_active=const_business.IS_ACTIVE_DELETED)

    return stmt


def stmt_query_will(
        will_slug: Optional[str] = None):

    stmt = select(
        WillModel
    )

    if will_slug:
        stmt = stmt.where(
            WillModel.will_slug == will_slug
        )

    return stmt



def stmt_query_immovable_asset(
        immovable_asset_slug: Optional[str] = None,
        asset_type: Optional[StringFilter] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES):

    stmt = select(
        ImmovableAssetModel
    ).where(
        ImmovableAssetModel.is_active == is_active
    )

    if immovable_asset_slug:
        stmt = stmt.where(
            ImmovableAssetModel.immovable_asset_slug == immovable_asset_slug
        )

    if asset_type:
        stmt = stmt.where(
            prepare_where_expression(
                field=ImmovableAssetModel.asset_type, operator=asset_type.operator.value, value=asset_type.value
            )
        )

    stmt = stmt.order_by(ImmovableAssetModel.immovable_asset_id)

    return stmt


def stmt_query_user_people(user_id: Optional[int] = None, people_id: Optional[int] = None):

    stmt = select(
        UserPeopleModel
    ).where(
        UserPeopleModel.is_active == const_business.IS_ACTIVE_YES,
    )

    if user_id:
        stmt = stmt.where(UserPeopleModel.user_id == user_id)

    if people_id:
        stmt = stmt.where(UserPeopleModel.people_id == people_id)

    return stmt


def stmt_query_people(people_id: Optional[int] = None, people_slug: Optional[str] = None):

    stmt = select(
        PeopleModel
    ).where(
        PeopleModel.is_active == const_business.IS_ACTIVE_YES,
    )

    if people_id:
        stmt = stmt.where(PeopleModel.people_id == people_id)

    if people_slug:
        stmt = stmt.where(PeopleModel.people_slug == people_slug)

    return stmt


def stmt_query_latest_people_identity(people_id: int):

    return select(
        PeopleIdentityModel
    ).where(
        PeopleIdentityModel.people_id == people_id,
        PeopleIdentityModel.is_active == const_business.IS_ACTIVE_YES,
    ).order_by(
        desc(PeopleIdentityModel.people_identity_id)
    ).limit(1)


def stmt_delete_people_identity(where: dict, updated_by: int):

    stmt = update(PeopleIdentityModel)

    #
    # Build Where conditions
    for field, value in where.items():
        stmt = stmt.where(getattr(PeopleIdentityModel, field) == value)

    #
    # Build susbtitute values
    stmt = stmt.values(
        updated_by=updated_by,
        is_active=const_business.IS_ACTIVE_DELETED,
    )

    return stmt


def stmt_query_charity(charity_id: Optional[int] = None, charity_slug: Optional[str] = None):

    stmt = select(
        CharityModel
    ).where(
        CharityModel.is_active == const_business.IS_ACTIVE_YES,
    )

    if charity_id:
        stmt = stmt.where(CharityModel.charity_id == charity_id)

    if charity_slug:
        stmt = stmt.where(CharityModel.charity_slug == charity_slug)

    return stmt


def stmt_query_user_charity(user_id: Optional[int] = None, charity_id: Optional[int] = None):

    stmt = select(
        UserCharityModel
    ).where(
        UserCharityModel.is_active == const_business.IS_ACTIVE_YES
    )

    if user_id:
        stmt = stmt.where(UserCharityModel.user_id == user_id)

    if charity_id:
        stmt = stmt.where(UserCharityModel.charity_id == charity_id)

    return stmt


def stmt_query_print_request(
        user_id: Optional[int] = None,
        will_id: Optional[int] = None,
        status: Optional[list[str]] = None,
        print_request_slug: Optional[str] = None,
        is_active: Optional[str] = const_business.IS_ACTIVE_YES): 

    stmt = select(PrintRequestModel)

    if user_id:
        stmt = stmt.where(PrintRequestModel.user_id == user_id)
    
    if will_id:
        stmt = stmt.where(PrintRequestModel.will_id == will_id)

    if status:
        stmt = stmt.where(PrintRequestModel.status.in_(status))

    if print_request_slug:
        stmt = stmt.where(PrintRequestModel.print_request_slug == print_request_slug)

    if is_active:
        stmt = stmt.where(PrintRequestModel.is_active == is_active)

    stmt = stmt.order_by(PrintRequestModel.print_request_id)

    return stmt
