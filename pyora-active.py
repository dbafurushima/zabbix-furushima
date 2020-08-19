#!/usr/bin/env python
# coding: utf-8
# vim: tabstop=2 noexpandtab
"""
	Based on:
		https://github.com/bicofino/Pyora
	    Author: Danilo F. Chilene

		https://github.com/Lelik13a/Zabbix-PyOra-ActiveCheck
	    Author: Aleksey A.


	NEWPyOra - Carlos Furushima
	conventions and nomenclatures
		True / False values :
			0 - OK : True (Verdadeiro)
			1 - NOK : False (Falso)
"""

import argparse
import cx_Oracle
import inspect
import json
import re
from pyzabbix import ZabbixMetric, ZabbixSender
import pyora_config

version = 0.2


class Checks(object):
    def check_active(self):
        """Check Intance is active and open"""
        sql = "select to_char(case when inst_cnt > 0 then 1 else 0 end, \
              'FM99999999999999990') retvalue from (select count(*) inst_cnt \
              from v$instance where status = 'OPEN' and logins = 'ALLOWED' \
              and database_status = 'ACTIVE')"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def rcachehit(self):
        """Read Cache hit ratio"""
        sql = "SELECT to_char((1 - (phy.value - lob.value - dir.value) / \
              ses.value) * 100, 'FM99999990.9999') retvalue \
              FROM   v$sysstat ses, v$sysstat lob, \
              v$sysstat dir, v$sysstat phy \
              WHERE  ses.name = 'session logical reads' \
              AND    dir.name = 'physical reads direct' \
              AND    lob.name = 'physical reads direct (lob)' \
              AND    phy.name = 'physical reads'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dsksortratio(self):
        """Disk sorts ratio"""
        sql = "SELECT to_char(d.value/(d.value + m.value)*100, \
              'FM99999990.9999') retvalue \
              FROM  v$sysstat m, v$sysstat d \
              WHERE m.name = 'sorts (memory)' \
              AND d.name = 'sorts (disk)'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def activeusercount(self):
        """Count of active users"""
        sql = "select to_char(count(*)-1, 'FM99999999999999990') retvalue \
              from v$session where username is not null \
              and status='ACTIVE'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbsize(self):
        """Size of user data (without temp)"""
        #        sql = "SELECT to_char(sum(  NVL(a.bytes - NVL(f.bytes, 0), 0)), \
        #              'FM99999999999999990') retvalue \
        #              FROM sys.dba_tablespaces d, \
        #              (select tablespace_name, sum(bytes) bytes from dba_data_files \
        #              group by tablespace_name) a, \
        #              (select tablespace_name, sum(bytes) bytes from \
        #              dba_free_space group by tablespace_name) f \
        #              WHERE d.tablespace_name = a.tablespace_name(+) AND \
        #              d.tablespace_name = f.tablespace_name(+) \
        #              AND NOT (d.extent_management like 'LOCAL' AND d.contents \
        #              like 'TEMPORARY')"
        sql = "SELECT to_char(sum(  NVL(a.bytes - NVL(f.bytes, 0), 0)), 'FM99999999999999990') retvalue \
                 FROM sys.dba_tablespaces d, \
                 (select tablespace_name, sum(bytes) bytes from dba_data_files group by tablespace_name) a, \
                 (select tablespace_name, sum(bytes) bytes from dba_free_space group by tablespace_name) f \
                 WHERE d.tablespace_name = a.tablespace_name(+) AND d.tablespace_name = f.tablespace_name(+) \
                 AND NOT (d.extent_management like 'LOCAL' AND d.contents like 'TEMPORARY')"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbfilesize(self):
        """Size of all datafiles"""
        sql = "select to_char(sum(bytes), 'FM99999999999999990') retvalue \
              from dba_data_files"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def version(self):
        """Oracle version (Banner)"""
        sql = "select banner from v$version where rownum=1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def uptime(self):
        """Instance Uptime (seconds)"""
        sql = "select to_char((sysdate-startup_time)*86400, \
              'FM99999999999999990') retvalue from v$instance"

        self.cur.execute(sql)
        res = self.cur.fetchmany(numRows=3)
        for i in res:
            return i[0]

    def commits(self):
        """User Commits"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'user commits'"

        self.cur.execute(sql)
        res = self.cur.fetchmany(numRows=3)
        for i in res:
            return i[0]

    def rollbacks(self):
        """User Rollbacks"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'user rollbacks'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def deadlocks(self):
        """Deadlocks"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'enqueue deadlocks'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def redowrites(self):
        """Redo Writes"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'redo writes'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def tblscans(self):
        """Table scans (long tables)"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'table scans (long tables)'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def tblrowsscans(self):
        """Table scan rows gotten"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'table scan rows gotten'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def indexffs(self):
        """Index fast full scans (full)"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'index fast full scans (full)'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def hparsratio(self):
        """Hard parse ratio"""
        sql = "SELECT to_char(h.value/t.value*100,'FM99999990.9999') \
              retvalue FROM  v$sysstat h, v$sysstat t WHERE h.name = 'parse count (hard)' AND t.name = 'parse count (total)'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        print res
        for i in res:
            return i[0]

    def netsent(self):
        """Bytes sent via SQL*Net to client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'bytes sent via SQL*Net to client'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def netresv(self):
        """Bytes received via SQL*Net from client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'bytes received via SQL*Net from client'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def netroundtrips(self):
        """SQL*Net roundtrips to/from client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'SQL*Net roundtrips to/from client'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def logonscurrent(self):
        """Logons current"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'logons current'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def lastarclog(self):
        """Last archived log sequence"""
        sql = "select to_char(max(SEQUENCE#), 'FM99999999999999990') \
              retvalue from v$log where archived = 'YES'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def lastapplarclog(self):
        """Last applied archive log (at standby).Next items requires [timed_statistics = true]"""
        sql = "select to_char(max(lh.SEQUENCE#), 'FM99999999999999990') \
              retvalue from v$loghist lh, v$archived_log al \
              where lh.SEQUENCE# = al.SEQUENCE# and applied='YES'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def freebufwaits(self):
        """Free buffer waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'free buffer waits'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def bufbusywaits(self):
        """Buffer busy waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) = \
              en.name and en.name = 'buffer busy waits'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def logswcompletion(self):
        """log file switch completion"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'log file switch completion'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def logfilesync(self):
        """Log file sync"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'log file sync'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def logprllwrite(self):
        """Log file parallel write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'log file parallel write'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def enqueue(self):
        """Enqueue waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'enqueue'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbseqread(self):
        """DB file sequential read waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file sequential read'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbscattread(self):
        """DB file scattered read"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file scattered read'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbsnglwrite(self):
        """DB file single write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file single write'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def dbprllwrite(self):
        """DB file parallel write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file parallel write'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def directread(self):
        """Direct path read"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'direct path read'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def directwrite(self):
        """Direct path write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'direct path write'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def latchfree(self):
        """latch free"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'latch free'"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def tablespace(self, name):
        """Get tablespace usage"""
        #        sql='''SELECT  tablespace_name,
        #        100-(TRUNC((max_free_mb/max_size_mb) * 100)) AS USED
        #        FROM ( SELECT a.tablespace_name,b.size_mb,a.free_mb,b.max_size_mb,a.free_mb + (b.max_size_mb - b.size_mb) AS max_free_mb
        #        FROM   (SELECT tablespace_name,TRUNC(SUM(bytes)/1024/1024) AS free_mb FROM dba_free_space GROUP BY tablespace_name) a,
        #        (SELECT tablespace_name,TRUNC(SUM(bytes)/1024/1024) AS size_mb,TRUNC(SUM(GREATEST(bytes,maxbytes))/1024/1024) AS max_size_mb
        #        FROM   dba_data_files GROUP BY tablespace_name) b WHERE  a.tablespace_name = b.tablespace_name
        #        ) where tablespace_name='{0}' order by 1'''.format('ZH')
        sql = '''SELECT tablespace_name "TABLESPACE", used_percent "USED" FROM dba_tablespace_usage_metrics WHERE tablespace_name = '{0}' '''.format(
            name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[1]

#    def tablespace_abs(self, name):
#        """Get tablespace in use"""
        #        sql = '''SELECT df.tablespace_name "TABLESPACE", (df.totalspace - \
        #              tu.totalusedspace) "FREEMB" from (select tablespace_name, \
        #              sum(bytes) TotalSpace from dba_data_files group by tablespace_name) \
        #              df ,(select sum(bytes) totalusedspace,tablespace_name from dba_segments \
        #              group by tablespace_name) tu WHERE tu.tablespace_name = \
        #              df.tablespace_name and df.tablespace_name = '{0}' '''.format(name)
#        sql = '''SELECT tablespace_name "TABLESPACE", round(used_space * 8192, 2) "BYTES" FROM dba_tablespace_usage_metrics  WHERE  tablespace_name = '{0}' '''.format(
#            name)
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        for i in res:
#            return i[1]

    def check_archive(self, archive):
        """List archive used"""
        sql = "select trunc((total_mb-free_mb)*100/(total_mb)) PCT from \
              v$asm_diskgroup_stat where name='{0}' \
              ORDER BY 1".format(archive)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

#    def asm_volume_use(self, name):
#        """Get ASM volume usage"""
#        sql = "select round(((TOTAL_MB-FREE_MB)/TOTAL_MB*100),2) from \
#              v$asm_diskgroup_stat where name = '{0}'".format(name)
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        for i in res:
#            return i[0]
#
#    def asm_volume_size(self, name):
#        sql = "select TOTAL_MB from v$asm_diskgroup_stat where name = '{0}'".format(
#            name)
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        for i in res:
#            return i[0]
#
#    def asm_volume_free(self, name):
#        sql = "select FREE_MB from v$asm_diskgroup_stat where name = '{0}'".format(
#            name)
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        for i in res:
#            return i[0]
#

    def query_lock(self):
        """Query lock"""
        sql = "select count(*) from gv$lock l1, gv$session s1, gv$lock l2, gv$session s2   \
	       where s1.sid=l1.sid and s2.sid=l2.sid and s1.inst_id=l1.inst_id and s2.inst_id=l2.inst_id   \
               and l1.BLOCK=1 and l2.request > 0   and l1.id1 = l2.id1   \
               and l2.id2 = l2.id2 and s1.last_call_et > 300 and rownum = 1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

#    def query_lock_list(self):
#        '''Query lock list'''
#        sql = "SELECT DECODE(request,0,'Holder: ','Waiter: ')|| sid sess, id1, id2, lmode, request, type FROM V$LOCK WHERE (id1, id2, type) IN (SELECT id1, id2, type FROM V$LOCK WHERE request>0) ORDER BY id1, request"
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        ans = "\n"
#        for i in res:
#            ans = ans + str(i) + "\n"
#        sql = "select sb.BLOCKER_SID HOLDER, sb.SID WAITER, v.USERNAME, v.CLIENT_IDENTIFIER, v.PROGRAM, v.STATUS, do.object_name, sq.SQL_TEXT from v$session_blockers sb, v$session v, v$sql sq, v$locked_object lo, dba_objects do where sb.sid = v.sid and v.SQL_ID = sq.SQL_ID and lo.SESSION_ID = v.SID and do.object_id = lo.OBJECT_ID"
#        self.cur.execute(sql)
#        res = self.cur.fetchall()
#        for i in res:
#            ans = ans + str(i) + "\n"
#        return ans
#
    def query_lock_list2(self):
        '''Query lock list 2'''
        sql = "SELECT 'Host '|| s1.CLIENT_IDENTIFIER || ', User ' ||s1.username || ' ( SID= ' || s1.sid || ' ) with the statement: ' || sqlt2.sql_text ||' |is blocking ' || s2.username || ' ( SID=' || s2.sid || ' ) SQL -> ' ||sqlt1.sql_text AS blocking_status FROM v$lock l1, v$session s1 ,v$lock l2 ,v$session s2 ,v$sql sqlt1 ,v$sql sqlt2 WHERE s1.sid =l1.sid AND s2.sid =l2.sid AND sqlt1.sql_id= s2.sql_id AND sqlt2.sql_id= s1.prev_sql_id AND l1.BLOCK =1 AND l2.request > 0 AND l1.id1 = l2.id1 AND l2.id2 = l2.id2"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        ans = "\n"
        for i in res:
            ans = ans + str(i) + "\n"
        ans = ans.replace("|", "\n\t")
        sql = "select sb.BLOCKER_SID HOLDER, sb.SID WAITER, v.USERNAME, v.CLIENT_IDENTIFIER, v.PROGRAM, v.STATUS, do.object_name,sb.WAIT_EVENT_TEXT, sq.SQL_TEXT from v$session_blockers sb, v$session v, v$sql sq, v$locked_object lo, dba_objects do where sb.sid = v.sid and v.SQL_ID = sq.SQL_ID and lo.SESSION_ID = v.SID and do.object_id = lo.OBJECT_ID"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        ans = ans + "\n"
        for i in res:
            ans = ans + str(i) + "\n"
        return ans


    def query_redologs(self):
        """Redo logs"""
        sql = "select COUNT(*) from v$LOG WHERE STATUS='ACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def query_rollbacks(self):
        """Query Rollback"""
        sql = "select nvl(trunc(sum(used_ublk*4096)/1024/1024),0) from \
              gv$transaction t,gv$session s where ses_addr = saddr"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def query_sessions(self):
        """Query Sessions"""
#        sql = "select count(*) from gv$session where username is not null and status='ACTIVE'"
        sql = "select CASE WHEN to_number(proc) < target  THEN 0 ELSE 1 end from (select max(cntproc) proc from ( select inst_id ,  count(*) as cntproc from  gv$session group by inst_id ) ) a , (select process * 0.80  as target from (select distinct  min(VALUE) as process from gv$parameter where NAME='processes') ) b"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def query_sessions_active(self):
        """Query Sessions"""
#        sql = "select count(*) from gv$session where username is not null and status='ACTIVE'"
        sql = "select count(*) from gv$session where status='ACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]


    def query_sessions_inactive(self):
        """Query Sessions"""
#        sql = "select count(*) from gv$session where username is not null and status='ACTIVE'"
        sql = "select count(*) from gv$session where status='INACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]


    def query_sessions_total(self):
        """Query Sessions"""
#        sql = "select count(*) from gv$session where username is not null and status='ACTIVE'"
        sql = "select count(*) from gv$session "
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]



    def redo_checkpoint_not_complete(self):
        """Query Sessions"""
        sql = "select CASE WHEN to_number(CAST (max(HITREDO) AS INTEGER)) < 70 THEN 0 ELSE 1 end  from  (SELECT l.thread#, to_number((to_number (count(*) * 100))/(select count(*) from v$log)) as HITREDO ,  count(*) redoanalic FROM   v$log l   where l.status not in ('INACTIVE') group by l.thread# )"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]


    def tablespace_temp(self, name):
        """Query temporary tablespaces"""
        sql = "SELECT round(((TABLESPACE_SIZE-FREE_SPACE)/TABLESPACE_SIZE)*100,2) \
              PERCENTUAL FROM dba_temp_free_space where \
              tablespace_name='{0}'".format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def query_sysmetrics(self, name):
        """Query v$sysmetric parameters"""
        sql = "select value from v$sysmetric where METRIC_NAME ='{0}' and \
              rownum <=1 order by INTSIZE_CSEC".format(name.replace('_', ' '))
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def fra_use(self):
        """Query the Fast Recovery Area usage"""
        sql = "select round((SPACE_LIMIT-(SPACE_LIMIT-SPACE_USED))/ \
              SPACE_LIMIT*100,2) FROM V$RECOVERY_FILE_DEST"

        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def user_status(self, dbuser):
        """Determines whether a user is locked or not"""
        sql = "SELECT account_status FROM dba_users WHERE username='{0}'" \
            .format(dbuser)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]

    def user_open_cursors(self):
        """Show open cursors count"""
        sql = "select count(*) from v$open_cursor where sid in (select sys_context('userenv','sid') from dual)"
        self.cur.prepare(sql)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            return i[0]



########################## NUNCA MAIS EU MEXO!!!!

class Main(Checks):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '--address', required=True, help="Oracle database address")
        parser.add_argument(
            '--database', required=True, help="Oracle database SID")
        parser.add_argument('--username', help="Oracle database user")
        parser.add_argument(
            '--password', help="Oracle database user's password")
        parser.add_argument(
            '--port', default=1521, help="Oracle database port")
        parser.add_argument(
            '--ora1000',
            action='store_true',
            help="reconnect to Oracle database when request tablespace's size (bug 17897511)"
        )
        parser.add_argument(
            '--verbose',
            '-v',
            action='store_true',
            help="Additional verbose information")

        self.args = parser.parse_args()

        if self.args.username is None:
            self.args.username = pyora_config.username
        if self.args.password is None:
            self.args.password = pyora_config.password

    def db_connect(self):
        dsn = cx_Oracle.makedsn(self.args.address, self.args.port,
                                self.args.database)
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
            self.db_connect()
        except Exception, err:
            print str(err)
            return 1

        Data = []
        try:
            with open("/usr/lib/zabbix/cache/items-" + self.args.address + "-"
                      + self.args.database + ".list") as keylist:
                for key in keylist:
                    key = key.split(',')
                    hostname = key[0]
                    keyname = key[1].rstrip('\n')

                    key = keyname.split('[')

                    # Oracle bug 17897511 (ORA-1000 from query on DBA_TABLESPACE_USAGE_METRICS)
                    if (key[0] == "tablespace" or
                            key[0] == "tablespace_abs") and self.args.ora1000:
                        self.db_close()
                        self.db_connect()

                    if len(key) > 1:
                        key[1] = key[1].rstrip(']')
                        if self.args.verbose:
                            print "Processing: " + key[0] + ": " + key[1]
                        value = getattr(Checks, key[0])(self, key[1])
                        if self.args.verbose:
                            print "\t\t\t" + str(value)
                    else:
                        if self.args.verbose:
                            print "Processing: " + key[0]
                        value = getattr(Checks, key[0])(self)
                        if self.args.verbose:
                            print "\t\t\t" + str(value)

                    Data.append(ZabbixMetric(hostname, keyname, value))
                    if self.args.verbose:
                        print "Data to send:"
                        print Data
                        result = ZabbixSender(use_config=True).send(Data)
                        print result
                        print "\n"
                        Data = []

            if not self.args.verbose:
                result = ZabbixSender(use_config=True).send(Data)
                print result
                Data = []
                Data.append(
                    ZabbixMetric(hostname, "failedchecks", result.failed))
                result = ZabbixSender(use_config=True).send(Data)
                print result

        except IOError, err:
            print str(err)

        finally:
            self.db_close()

if __name__ == "__main__":
    main = Main()
    main()
