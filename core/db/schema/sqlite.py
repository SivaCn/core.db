# -*- coding: utf-8 -*-

"""

    Module :mod:``


    LICENSE: The End User license agreement is located at the entry level.

"""

# ----------- START: Native Imports ---------- #
import sqlite3 as sqlite
# ----------- END: Native Imports ---------- #

# ----------- START: Third Party Imports ---------- #
# ----------- END: Third Party Imports ---------- #

# ----------- START: In-App Imports ---------- #
from core.db import DataBaseEntity
# ----------- END: In-App Imports ---------- #

__all__ = [
    # All public symbols go here.
]


#conn = sqlite.connect(r"db.sqlite")
#conn.close()


DataBaseEntity(
    query='''PRAGMA foreign_keys = ON;''',
    desc='''pre condition'''
)

DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."code_schedule_type" ('''
        '''schedule_type_idn INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,'''
        '''schedule_type VARCHAR NOT NULL ,'''
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,'''
        '''upd_dt DATETIME NOT NULL)'''
    ),
    desc='''Create code_schedule_type table''',
    pre_query='''DROP TABLE IF EXISTS CODE_SCHEDULE_TYPE'''
)

DataBaseEntity(
    query='''INSERT INTO "main"."code_schedule_type" ("schedule_type","crt_dt","upd_dt") VALUES ('OneTime',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_schedule_type table'''
)

DataBaseEntity(
    query='''INSERT INTO "main"."code_schedule_type" ("schedule_type","crt_dt","upd_dt") VALUES ('Daily',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_schedule_type table'''
)

DataBaseEntity(
    query='''INSERT INTO "main"."code_schedule_type" ("schedule_type","crt_dt","upd_dt") VALUES ('Weekly',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_schedule_type table'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."code_status" ('''
        '''status_idn INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,'''
        '''status VARCHAR NOT NULL  UNIQUE ,'''
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,'''
        '''upd_dt DATETIME NOT NULL)'''
    ),
    desc='''Create code_status table''',
    pre_query='''DROP TABLE IF EXISTS CODE_STATUS'''
)


DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('success',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('failure',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('error',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('loggedin',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('loggedout',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('timedout',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('initiated',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('inprocess',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('completed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('missed',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)
DataBaseEntity(
    query='''INSERT INTO "main"."code_status" ("status","crt_dt","upd_dt") VALUES ('pending',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP);''',
    desc='''Data Load for code_status table'''
)


DataBaseEntity(
    query=(
        '''CREATE TABLE IF NOT EXISTS user ('''
        '''user_idn INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,'''
        '''first_name varchar(25) NOT NULL,'''
        '''last_name varchar(25),'''
        '''user_name varchar(25) NOT NULL,'''
        '''hash1 VARCHAR(64) NOT NULL,'''
        '''hash2 VARCHAR(64),'''
        '''phone_no1 number NOT NULL,'''
        '''phone_no2 number,'''
        '''email_id varchar(50),'''
        '''crt_dt DATETIME,'''
        '''upd_dt DATETIME,'''
        '''is_active number(1) DEFAULT 1)'''
    ),
    desc='''Create User table''',
    pre_query='''DROP TABLE IF EXISTS USER'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."user_session" ('''
        '''"user_session_idn" INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,'''
        '''"user_idn" INTEGER NOT NULL ,'''
        '''"client_ip" VARCHAR NOT NULL ,'''
        '''"browser_name" VARCHAR,'''
        '''"browser_version" VARCHAR,'''
        '''"attempted_on" DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,'''
        '''"status_idn" INTEGER NOT NULL,'''
        '''"is_active" INTEGER DEFAULT 1,'''
        '''"unique_session_cd" VARCHAR DEFAULT (null),'''
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, '''
        '''upd_dt DATETIME DEFAULT CURRENT_TIMESTAMP, '''
        '''    FOREIGN KEY(user_idn) REFERENCES user(user_idn),'''
        '''    FOREIGN KEY(status_idn) REFERENCES code_status(status_idn))'''
    ),
    desc='''Create user_session table''',
    pre_query='''DROP TABLE IF EXISTS USER_SESSION'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."user_activity" ('''
        '''user_activity_idn INTEGER PRIMARY KEY  AUTOINCREMENT  NOT NULL ,'''
        '''is_authorized INTEGER NOT NULL ,'''
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,'''
        '''status_idn INTEGER NOT NULL ,'''
        '''user_session_idn INTEGER NOT NULL,'''
        #'''FOREIGN KEY(user_idn) REFERENCES user(user_idn),'''
        '''    FOREIGN KEY(status_idn) REFERENCES code_status(status_idn),'''
        '''    FOREIGN KEY(user_session_idn) REFERENCES user_session(user_session_idn))'''
    ),
    desc='''Create user_activity table''',
    pre_query='''DROP TABLE IF EXISTS USER_ACTIVITY'''
)


DataBaseEntity(
    query=(
        '''    CREATE  TABLE  IF NOT EXISTS "main"."job_details" '''
        '''    (job_details_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''    job_id VARCHAR NOT NULL , '''
        '''    schedule_type_idn INTEGER NOT NULL, '''
        '''    start_date DATETIME NOT NULL , '''
        '''    recurrence VARCHAR, '''
        '''    day_of_week VARCHAR, '''
        '''    params VARCHAR, '''
        '''    next_run_time VARCHAR, '''
        '''    is_active INTEGER NOT NULL DEFAULT 1, '''
        '''    user_idn INTEGER NOT NULL , '''
        '''    crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, '''
        '''    upd_dt DATETIME DEFAULT CURRENT_TIMESTAMP, '''
        '''        FOREIGN KEY(user_idn) REFERENCES user(user_idn), '''
        '''        FOREIGN KEY(schedule_type_idn) REFERENCES code_schedule_type(schedule_type_idn)) '''
    ),
    desc='''Create job_details table''',
    pre_query='''DROP TABLE IF EXISTS JOB_DETAILS'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."job_run_log" '''
        '''(job_run_log_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''job_id VARCHAR NOT NULL , '''
        '''status_idn INTEGER NOT NULL ,''' 
        '''message VARCHAR, '''
        '''error_trace VARCHAR,''' 
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, '''
        '''upd_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP,'''
        '''    FOREIGN KEY(job_id) REFERENCES job_details(job_id),'''
        '''    FOREIGN KEY(status_idn) REFERENCES code_status(status_idn))'''
    ),
    desc='''Create job_run_log table''',
    pre_query='''DROP TABLE IF EXISTS JOB_RUN_LOG'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."trans_otp" '''
        '''(trans_otp_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''otp_code INTEGER NOT NULL , '''
        '''user_idn INTEGER NOT NULL , '''
        '''status_idn INTEGER NOT NULL ,''' 
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, '''
        '''    FOREIGN KEY(user_idn) REFERENCES user(user_idn),'''
        '''    FOREIGN KEY(status_idn) REFERENCES code_status(status_idn))'''
    ),
    desc='''Create trans_otp table''',
    pre_query='''DROP TABLE IF EXISTS TRANS_OTP'''
)

DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."trans_sms" '''
        '''(trans_sms_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''message VARCHAR , '''
        '''user_idn INTEGER NOT NULL , ''' 
        '''crt_dt DATETIME NOT NULL  DEFAULT CURRENT_TIMESTAMP, '''
        '''    FOREIGN KEY(user_idn) REFERENCES user(user_idn))'''
    ),
    desc='''Create trans_sms table''',
    pre_query='''DROP TABLE IF EXISTS TRANS_SMS'''
)

DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."code_events" '''
        '''(code_events_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''event_name VARCHAR NOT NULL  UNIQUE) '''
    ),
    desc='''Create code_events table''',
    pre_query='''DROP TABLE IF EXISTS CODE_EVENTS'''
)

DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."code_sms_events" '''
        '''(code_sms_events_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''code_events_idn INTEGER , '''
        '''is_active NUMERIC NOT NULL  DEFAULT 1, '''
        '''    FOREIGN KEY(code_events_idn) REFERENCES code_events(code_events_idn))'''
    ),
    desc='''Create code_sms_events table''',
    pre_query='''DROP TABLE IF EXISTS CODE_SMS_EVENTS'''
)


DataBaseEntity(
    query=(
        '''CREATE  TABLE  IF NOT EXISTS "main"."config_user_sms" '''
        '''(config_user_sms_idn INTEGER PRIMARY KEY  NOT NULL  UNIQUE , '''
        '''user_idn INTEGER NOT NULL , '''
        '''code_sms_events_idn INTEGER , '''
        '''is_active NUMERIC NOT NULL  DEFAULT 1, '''
        '''    FOREIGN KEY(user_idn) REFERENCES user(user_idn),'''
        '''    FOREIGN KEY(code_sms_events_idn) REFERENCES code_events(code_sms_events_idn))'''
    ),
    desc='''Create config_user_sms table''',
    pre_query='''DROP TABLE IF EXISTS CONFIG_USER_SMS'''
)


