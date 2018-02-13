# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #

# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db.saorm import SqlAlchemyORM
from core.db.entity import (
    UserEntity, UserSessionEntity, CodeStatusEntity, UserActivityEntity
)
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


class UserModel(SqlAlchemyORM):
    table = UserEntity

    @classmethod
    def fetch_user_data(cls, session, mode='all', **kwargs):
        modes = ('all', 'one', )
        if mode not in modes:
            raise Exception("Argument mode is not one among {}".format(modes))

        if mode == 'all':
            return cls.fetch(session, **kwargs)
        elif mode == 'one':
            return cls.fetch_one(session, **kwargs)

    @classmethod
    def user_exists(cls, session, **kwargs):
        return True if cls.fetch(session, **kwargs) else False

    @classmethod
    def create_new_user(cls, session, **kwargs):
        return cls.insert(session, **kwargs)

class CodeStatusModel(SqlAlchemyORM):
    table = CodeStatusEntity

    @classmethod
    def fetch_status_idn(cls, session, **kwargs):
        return cls.fetch_one(session, **kwargs)

class UserSessionModel(SqlAlchemyORM):
    table = UserSessionEntity

    @classmethod
    def create_user_session(cls, session, **kwargs):
        return cls.insert(session, **kwargs)

    @classmethod
    def logout(cls, session, user_idn, user_session_cd):
        code_status_data = CodeStatusModel.fetch_status_idn(session, status='loggedout')

        return cls.update(
            session,
            updates={'is_active': 0, 'status_idn': code_status_data.status_idn},
            where_condition={'user_idn': user_idn, 'unique_session_cd': user_session_cd}
        )

    @classmethod
    def fetch_active_loggedin_user_session(cls, session, mode='all', select_cols="*", data_as_dict=False, **kwargs):
        kwargs.update({'join_tables':list()})

        if 'is_active' not in kwargs:
            kwargs['is_active'] = 1

        if 'status' not in kwargs:
            code_status_data = CodeStatusModel.fetch_status_idn(session, status='loggedin')
            kwargs['status_idn'] = code_status_data.status_idn

        if 'user_idn' in kwargs:
            kwargs['join_tables'].append(
                cls.join_construct(
                    table_model=UserModel,
                    join_on='default',
                    where_condition={'user_idn': kwargs.pop('user_idn')}
                )
            )

        return super(cls, cls).fetch(
            session, mode=mode, select_cols=select_cols, data_as_dict=data_as_dict, **kwargs
        )

class UserActivityModel(SqlAlchemyORM):
    table = UserActivityEntity

    @classmethod
    def create_user_activity(cls, session, **kwargs):
        return cls.insert(session, **kwargs)


