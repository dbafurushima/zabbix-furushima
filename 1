export SCRIPT_HOME=/stage/script_zabbix
export OPERATION=$1
export HOST_ZABBIX=$(echo $2 | tr '[:lower:]' '[:upper:]')      #DATABASE_PRD1
export HOSTNAME=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].hostname' | /usr/bin/strings)
export DATABASE=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].instance' | /usr/bin/strings)
export PORT=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].port' | /usr/bin/strings)
export USER=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$1'})
export PASSWORD=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$2'})

