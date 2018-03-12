# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
__import__('pkg_resources').declare_namespace(__name__)
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.utils.environ import get_main_db_details
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


main_db_details = get_main_db_details()


class DataBaseEntity(object):
    """."""
    instances = list()

    def __init__(self, query, pre_query='', desc=''):
        """."""

        self.query = query
        self.pre_query = pre_query or None
        self.description = desc

        self.__class__.instances.append(self)

    @classmethod
    def load_all(cls):
        import sqlite3 as sqlite
        connection = sqlite.connect(main_db_details['path'])
        print "Database {} has been created sucessfully".format(main_db_details['name'])

        cursor = connection.cursor()

        for each in cls.instances:
            if each.description:
                print "Performing {}".format(each.description)
            if each.pre_query:
                print 'performing PRE-PROCESS for {}... '.format(each.description or '<NO DESC>'),
                try:
                    cursor.execute(each.pre_query)
                except:
                    print 'FAILURE'
                else:
                    print 'SUCCESS'

            print 'performing PROCESS for {}... '.format(each.description or '<NO DESC>'),
            try:
                cursor.execute(each.query)
            except:
                print 'FAILURE'
            else:
                print 'SUCCESS'

        connection.commit()


def create_session():
    """."""

    Session = sessionmaker()

    engine = create_engine('sqlite:///{}'.format(main_db_details['path']))
    Session.configure(bind=engine)

    return Session()
