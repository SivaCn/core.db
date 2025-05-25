# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
from sqlalchemy.inspection import inspect
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #

# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


def model_as_dict(model_instance):
    """Convert an SQLAlchemy model instance to a dictionary (excluding _sa_instance_state)."""

    return {
        column.key: getattr(model_instance, column.key)
        for column in inspect(model_instance).mapper.column_attrs
    }

