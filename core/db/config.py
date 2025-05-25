# -*- coding: utf-8 -*-

"""

    Module :mod:``

    This Module is created to...

    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import uuid

from datetime import datetime, UTC
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import pytz

import sqlalchemy as sa
from sqlalchemy.orm.session import Session
from sqlalchemy.schema import CreateColumn
from sqlalchemy.ext.compiler import compiles

from sqlalchemy.dialects.postgresql import UUID
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]

#
# A Schema stores all the configuration and business tables other than transactional ones.
BASE_SCHEMA = 'base_schema'


#
# User Unique Ids
SUPER_ADMIN_SLUG = '4004a730-cf97-4fdd-9ff1-610477d79b03'


#
# Role Unique ids
ROLE_SUPER_ADMIN_SLUG = '43ba52d7-8e25-4677-b77b-6dd4dacca35d'
ROLE_ADMIN_SLUG = '09cd4dc7-63a0-404b-a9ad-f6df655d0b95'
ROLE_CONTENT_SLUG = '445e4d95-c736-47d7-9cb9-a68a7caeab9f'
ROLE_OPERATIONS_SLUG = '0f9f81df-8448-4697-a352-383c267df2b4'


#
# Super Admin Configurations
SUPER_ADMIN = {
    'name': 'Eng Admin',
    'slug': SUPER_ADMIN_SLUG,
    'description': '',
    'password_hash': '$argon2id$v=19$m=102400,t=3,p=4$jZES4nwPwXgPYUypFeJcCw$cZlkKjQ6gCp2+Q23hzLxOTImtbfq5QevNGVyEa1opUg',
    'email': 'admin.eng@getyellow.in',
    'roles': [
        ROLE_SUPER_ADMIN_SLUG
    ]
}


