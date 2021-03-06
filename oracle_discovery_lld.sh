#!/bin/bash

export TIMESTAMP=`date "+%d-%m-%Y %H:%M:%S"`

export OP_ZBX=$1
export HOST_ZBX=$2
export PARAMETER=$3

export EXTERNAL_SCRIPT=/usr/lib/zabbix/externalscripts
LINE=$(cat /etc/zabbix/zabbix_server.conf | grep -i "LogFile=" | grep -iv "#" | awk -F"=" {'print$2'})
LINE=${LINE%/*}

# LOG
export LOG_D=$LINE/zabbix_pyora_discovery.log
export LOG=$LINE/zabbix_pyora.log
touch $LOG_D $LOG

echo $TIMESTAMP >> $LOG
echo "Operation Zabbix : " $OP_ZBX " HOSTNAME : " $HOST_ZBX " PARAMETER : " $PARAMETER >> $LOG

#oracle_discovery_lld.sh discovery DATABASE_PRD1 tablespace

###### trap
if [ $OP_ZBX = 'trap' ] ; then
. $EXTERNAL_SCRIPT/oracle_zabbix.sh $OP_ZBX $HOST_ZBX $PARAMETER > /tmp/debug_oracle_zabbix
echo $ZBX_SPACEUSED
sleep 1
echo '' >> $LOG
exit 0
fi


###### discovery
if [ $OP_ZBX = 'discovery' ] ; then
ps -ef | grep -i oracle_discovery_lld.sh | egrep -iv "trap|grep" >> $LOG
pgrep -lf oracle_discovery_lld.sh | egrep -iv "trap|grep" >> $LOG
export EXEC_DISCOVERY_COUNT=$(pgrep -lf oracle_discovery_lld.sh | egrep -iv "trap|grep" | wc -l )
  if [ $EXEC_DISCOVERY_COUNT -gt 2 ] ; then
        echo "OP_ZBX = " $OP_ZBX " --> " $EXEC_DISCOVERY_COUNT >> $LOG
	echo '' >> $LOG
#  exit 1
  else
. $EXTERNAL_SCRIPT/oracle_zabbix.sh $OP_ZBX $HOST_ZBX $PARAMETER > /tmp/debug_oracle_zabbix_discovery
echo $TIMESTAMP >> $LOG_D
echo '' >> $LOG_D
echo '-----------------------------------------' >> $LOG_D
echo '' >> $LOG_D
cat /usr/lib/zabbix/externalscripts/json_discovery | tee -a $LOG_D
echo '' >> $LOG_D
echo '-----------------------------------------' >> $LOG_D
echo '' >> $LOG_D
  fi
fi
echo '' >> $LOG

