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
    RoleModel,
    UserRoleModel,

    MenuModel,
    MenuRoleModel,
)

from core.utils.constants import (
    const_business,
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


def stmt_roles_by_user_id(user_id: int):

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



def stmt_menu_list(role_id: int, parent_id: Optional[int] = None):
    """

    Usage:
        >>> cursor = await session.replica.execute(stmt_menu_list)
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

