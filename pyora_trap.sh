#!/bin/bash
. ~root/.bash_profile > /dev/null

export ADDRESS=$1
export DATABASE=$2
export PORT=$3

# /usr/lib/zabbix/externalscripts/pyora-active.py  --address cnudbadm01.centralnacionalunimed.com.br --database PRD11
export TEST_TELNET=$( </dev/tcp/$ADDRESS/$PORT && echo OPEN || echo CLOSED)



export SCRIPT_HOME=/usr/lib/zabbix/externalscripts
export EXTERNAL_SCRIPT=/usr/lib/zabbix/externalscripts
export HOST_ZABBIX=$(echo $2 | tr '[:lower:]' '[:upper:]')      #DATABASE_PRD1
export HOSTNAME=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].hostname' | /usr/bin/strings)
export DATABASE=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].instance' | /usr/bin/strings)
export PORT=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].port' | /usr/bin/strings)
export USER=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$1'})
export PASSWORD=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$2'})




if [ $TEST_TELNET = "CLOSED" ] ; then
zabbix_sender --zabbix-server=127.0.0.1  --host="DB_PRD1" --key="db.updown" --value="1"
fi


#zabbix_sender --zabbix-server=127.0.0.1  --host="DB_PRD1" --key="db.updown" --value="1"


# /usr/lib/zabbix/externalscripts/pyora-active.py  --address $ADDRESS --database $DATABASE
