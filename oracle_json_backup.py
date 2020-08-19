#!/usr/bin/env python
# coding: utf-8
# vim: tabstop=2 noexpandtab

import argparse
import cx_Oracle
import inspect
import json
import re

version = 0.2


class Checks(object):


    def backup_archive(self):
        """ Backup Arc - JSON """
        sql = "select 'ARCHIVELOG' , case when count(*) >= 1 then 'NOK'  when count(*) = 0 then 'OK' end    from v$rman_backup_job_details where INPUT_TYPE  in ('ARCHIVELOG') and END_TIME BETWEEN sysdate-5/60 and sysdate  and  STATUS not in ('COMPLETED','RUNNING')"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#TYPE}','{#STATUS}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})


    def backup_fullinc(self):
        """ Backup Arc - JSON """
        sql = "select 'FULL_INC' , DECODE (STATUS, 'COMPLETED' , 'OK' , 'RUNNING' , 'OK', 'NOK' ) as STATUS  from v$rman_backup_job_details where INPUT_TYPE  in ('DB INCR','DB FULL') and END_TIME in  (select max(END_TIME) from v$rman_backup_job_details  where INPUT_TYPE  in ('DB INCR','DB FULL') )"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#TYPE}','{#STATUS}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})



class Main(Checks):
    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--address')
        parser.add_argument('--database')
        parser.add_argument('--port')
        parser.add_argument('--username')
        parser.add_argument('--password')

        subparsers = parser.add_subparsers()

        for name in dir(self):
            if not name.startswith("_"):
                p = subparsers.add_parser(name)
                method = getattr(self, name)
                argnames = inspect.getargspec(method).args[1:]
                for argname in argnames:
                    p.add_argument(argname)
                p.set_defaults(func=method, argnames=argnames)
        self.args = parser.parse_args()
        #self.args.username = pyora_config.username
       #self.args.password = pyora_config.password

    def db_connect(self):
        dsn = cx_Oracle.makedsn(self.args.address, self.args.port, self.args.database)
#        dsn = cx_Oracle.makedsn(self.args.address, 1521, self.args.database)
        self.pool = cx_Oracle.SessionPool(
            user=self.args.username,
            password=self.args.password,
            dsn=dsn,
            min=1,
            max=3,
            increment=1)
        self.db = self.pool.acquire()
        self.cur = self.db.cursor()

    def db_close(self):
        self.cur.close()
        self.pool.release(self.db)

    def __call__(self):
        try:
            a = self.args
            callargs = [getattr(a, name) for name in a.argnames]
            self.db_connect()
            try:
                return self.args.func(*callargs)
            finally:
                self.db_close()
        except Exception, err:
            print 0
            print str(err)


if __name__ == "__main__":
    main = Main()
    main()
