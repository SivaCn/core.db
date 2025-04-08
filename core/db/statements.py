# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
from typing import Optional, List
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy import desc, or_, and_, update
from sqlalchemy.future import select
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.models import (
    UserModel,
    UserContactModel,

    RoleModel,
    UserRoleModel,

    UserInviteModel,

    MenuModel,
    MenuRoleModel,

    PlanModel,
    FeatureModel,
    PlanFeatureModel,
)

from core.utils.constants import (
    const_business,
)

from core.utils.helpers.date import (
    utc_now,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


def stmt_query_roles(is_active: Optional[bool] = None, name: Optional[List[str]] = None):

    stmt = select(RoleModel)

    if is_active is None:
        stmt = stmt.where(RoleModel.is_active == const_business.IS_ACTIVE_YES)

    elif isinstance(is_active, bool):
        _is_active = const_business.IS_ACTIVE_YES if is_active is True else const_business.IS_ACTIVE_NO
        stmt = stmt.where(RoleModel.is_active == _is_active)

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
        is_active: Optional[bool] = True,
        plan_slug: Optional[str] = None,
        name: Optional[str] = None,
        is_listable: Optional[bool] = None,
        category: Optional[List[str]] = None):

    stmt = select(PlanModel)

    if is_active is None:
        stmt = stmt.where(PlanModel.is_active == const_business.IS_ACTIVE_YES)

    elif isinstance(is_active, bool):
        _is_active = const_business.IS_ACTIVE_YES if is_active is True else const_business.IS_ACTIVE_NO
        stmt = stmt.where(PlanModel.is_active == _is_active)

    if plan_slug is not None:
        stmt = stmt.where(PlanModel.plan_slug == plan_slug)

    if name is not None:
        stmt = stmt.where(PlanModel.name.ilike(f'%{name}%'))

    if is_listable is not None:
        stmt = stmt.where(PlanModel.is_listable == is_listable)

    if category is not None:
        stmt = stmt.where(PlanModel.category == category)

    return stmt


def stmt_query_user_invite(email: Optional[str] = None, user_schema: Optional[dict] = None):

    stmt = select(UserInviteModel)

    if email:
        stmt = stmt.where(UserInviteModel.email == email)

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
        is_active: Optional[bool] = None):

    stmt = select(UserContactModel)

    if is_active is None:
        stmt = stmt.where(UserContactModel.is_active == const_business.IS_ACTIVE_YES)

    elif isinstance(is_active, bool):
        _is_active = const_business.IS_ACTIVE_YES if is_active is True else const_business.IS_ACTIVE_NO
        stmt = stmt.where(UserContactModel.is_active == _is_active)

    if user_id:
        stmt = stmt.where(UserContactModel.user_id == user_id)

    if category:
        stmt = stmt.where(UserContactModel.category == category)

    if value:
        stmt = stmt.where(UserContactModel.value == value)

    if is_primary:
        stmt = stmt.where(UserContactModel.is_primary == is_primary)

    return stmt

