#!/usr/bin/env python


import argparse
import cx_Oracle
import inspect
import json
import re
import os
import string
import sys



v_py_HOSTNAME = os.environ["HOSTNAME"]
v_py_DATABASE = os.environ["DATABASE"]
v_py_PORT = os.environ["PORT"]
v_py_USER = os.environ["USER"]
v_py_PASSWORD = os.environ["PASSWORD"]


dsn = cx_Oracle.makedsn(v_py_HOSTNAME, v_py_PORT, sid=v_py_DATABASE)

connect_string = cx_Oracle.connect(user=v_py_USER,password=v_py_PASSWORD,dsn=dsn)
con = cx_Oracle.connect(user=v_py_USER,password=v_py_PASSWORD,dsn=dsn)



def tablespace(dummy):
    #print connect_string
    #con = cx_Oracle.connect(user="zabbix",password="zabbix",dsn=dsn)
    #con = cx_Oracle.connect(connect_string)
    cur = con.cursor()
    sql = "select ROUND ( ( ( datafile.bytes  - NVL ( freespace.bytes, 0 ) ) / datafile.bytes ) * 100  ) USED  FROM dba_tablespaces ts  , (SELECT tablespace_name      , SUM ( bytes ) bytes FROM dba_free_space      GROUP BY tablespace_name    ) freespace  , (SELECT   COUNT ( 1 ) datafiles      , SUM ( bytes ) bytes      , tablespace_name      FROM dba_data_files      GROUP BY tablespace_name    ) datafile  WHERE freespace.tablespace_name (+) = ts.tablespace_name  AND datafile.tablespace_name (+)   = ts.tablespace_name and  datafile.bytes is not null   and ts.tablespace_name not in (select distinct value from gv$parameter where name='undo_tablespace') and ts.tablespace_name='{0}'".format(dummy)
    cur.execute(sql)
    res = cur.fetchall()
    final_result = [list(i) for i in res]
    print str(final_result).strip('[]')


parser = argparse.ArgumentParser()
parser.add_argument("--tablespace", help="Nome da Tablespace", type=tablespace,  action="store")
parser.add_argument("echo",nargs='*')
args = parser.parse_args()


