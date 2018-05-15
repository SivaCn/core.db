# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


Base = declarative_base()

class UserEntity(Base):
    __tablename__ = 'user'

    user_idn = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    user_name = Column(String, nullable=False)
    hash1 = Column(String, nullable=False)
    hash2 = Column(String, nullable=True)
    phone_no1 = Column(String, nullable=False)
    phone_no2 = Column(String, nullable=True)
    email_id = Column(String, nullable=True)
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    upd_dt = Column(DateTime, default=datetime.datetime.now)
    is_active = Column(Integer, nullable=True, default=1)
    email_id = Column(String, nullable=True)

    #user_session = relationship('UserSessionEntity')

class CodeStatusEntity(Base):
    __tablename__ = 'code_status'

    status_idn = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    upd_dt = Column(DateTime, default=datetime.datetime.now)

class UserSessionEntity(Base):
    __tablename__ = 'user_session'

    user_session_idn = Column(Integer, primary_key=True)
    user_idn = Column(Integer, ForeignKey('user.user_idn'))
    client_ip = Column(String, nullable=False)
    browser_name = Column(String, nullable=True)
    browser_version = Column(String, nullable=True)
    attempted_on = Column(DateTime, default=datetime.datetime.now)
    status_idn = Column(Integer, ForeignKey('code_status.status_idn'))
    unique_session_cd = Column(String, nullable=True)
    is_active = Column(Integer, nullable=False, default=1)

    #user_name = relationship('UserEntity')

class UserActivityEntity(Base):
    __tablename__ = 'user_activity'

    user_activity_idn = Column(Integer, primary_key=True)
    is_authorized = Column(Integer, nullable=False)
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    status_idn = Column(Integer, ForeignKey('code_status.status_idn'))
    user_session_idn = Column(Integer, ForeignKey('user_session.user_session_idn'))

class CodeScheduleTypeEntity(Base):
    __tablename__ = 'code_schedule_type'

    schedule_type_idn = Column(Integer, primary_key=True)
    schedule_type = Column(String, nullable=False)
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    upd_dt = Column(DateTime, default=datetime.datetime.now)

class JobDetailsEntity(Base):
    __tablename__ = 'job_details'

    job_details_idn = Column(Integer, primary_key=True)
    job_id = Column(String, nullable=False)
    schedule_type_idn = Column(Integer, ForeignKey('code_schedule_type.schedule_type_idn'))
    start_date = Column(DateTime, default=datetime.datetime.now)
    recurrence = Column(String, nullable=True)
    day_of_week = Column(String, nullable=True)
    params = Column(String, nullable=True)
    next_run_time = Column(String, nullable=True)
    is_active = Column(Integer, nullable=False, default=1)
    user_idn = Column(Integer, ForeignKey('user.user_idn'))
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    upd_dt = Column(DateTime, default=datetime.datetime.now)

class JobRunLogEntity(Base):
    __tablename__ = 'job_run_log'

    job_run_log_idn = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey('job_details.job_id'))
    status_idn = Column(Integer, ForeignKey('code_status.status_idn'))
    message = Column(String, nullable=True)
    error_trace = Column(String, nullable=True)
    crt_dt = Column(DateTime, default=datetime.datetime.now)
    upd_dt = Column(DateTime, default=datetime.datetime.now)

class TransOtpEntity(Base):
    __tablename__ = 'trans_otp'

    trans_otp_idn = Column(Integer, primary_key=True)
    otp_code = Column(Integer, nullable=False)
    status_idn = Column(Integer, ForeignKey('code_status.status_idn'))
    user_idn = Column(Integer, ForeignKey('user.user_idn'))
    crt_dt = Column(DateTime, default=datetime.datetime.now)

class TransSmsEntity(Base):
    __tablename__ = 'trans_sms'

    trans_sms_idn = Column(Integer, primary_key=True)
    message = Column(String, nullable=False)
    user_idn = Column(Integer, ForeignKey('user.user_idn'))
    crt_dt = Column(DateTime, default=datetime.datetime.now)

class CodeEventsEntity(Base):
    __tablename__ = 'code_events'

    code_events_idn = Column(Integer, primary_key=True)
    event_name = Column(String, nullable=False)

class CodeSmsEventsEntity(Base):
    __tablename__ = 'code_sms_events'

    code_sms_events_idn = Column(Integer, primary_key=True)
    code_events_idn = Column(Integer, ForeignKey('code_events.code_events_idn'))
    is_active = Column(Integer, nullable=False, default=1)

class ConfigUserSmsEntity(Base):
    __tablename__ = 'config_user_sms'

    config_user_sms_idn = Column(Integer, primary_key=True)
    user_idn = Column(Integer, ForeignKey('user.user_idn'))
    code_sms_events_idn = Column(Integer, ForeignKey('code_sms_events.code_sms_events_idn'))
    is_active = Column(Integer, nullable=False, default=1)

