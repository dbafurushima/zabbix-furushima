#!/bin/bash
. ~root/.bash_profile > /dev/null
/usr/lib/zabbix/externalscripts/pyora-active.py  --address cnudbadm01.centralnacionalunimed.com.br --database PRD11
#/usr/lib/zabbix/externalscripts/pyora-active.py  --address cnudbadm01.centralnacionalunimed.com.br --database PRD121

