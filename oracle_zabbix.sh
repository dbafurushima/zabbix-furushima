#!/bin/bash
. ~root/.bash_profile > /dev/null

export SCRIPT_HOME=/usr/lib/zabbix/externalscripts
export EXTERNAL_SCRIPT=/usr/lib/zabbix/externalscripts
export OPERATION=$1
export HOST_ZABBIX=$(echo $2 | tr '[:lower:]' '[:upper:]')      #DATABASE_PRD1
export HOSTNAME=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].hostname' | /usr/bin/strings)
export DATABASE=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].instance' | /usr/bin/strings)
export PORT=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'machine[1].port' | /usr/bin/strings)
export USER=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$1'})
export PASSWORD=$(cat ${SCRIPT_HOME}/JSON_TNS/${HOST_ZABBIX}.json | /usr/bin/jq -r .'credencial' | /usr/bin/strings |  base64 --decode | sort | uniq | awk -F" " {'print$2'})



echo "DEBUG" > /tmp/debug
echo script_home :  $SCRIPT_HOME >> /tmp/debug
echo operation : $OPERATION >> /tmp/debug
echo host_zabbix : $HOST_ZABBIX >> /tmp/debug
echo hostname : $HOSTNAME  >> /tmp/debug
echo database: $DATABASE >> /tmp/debug
echo port : $PORT >> /tmp/debug
echo user : $USER >> /tmp/debug
echo password : $PASSWORD >> /tmp/debug




zbtrap(){
#export TABLESPACE_SPACEUSED=$(/stage/script_zabbix/oracle_values_teste.py --tablespace $TABLESPACE_NAME | sed "s/'//g")
export TABLESPACE_SPACEUSED=$($SCRIPT_HOME/oracle_values.py --tablespace $TABLESPACE_NAME | sed "s/'//g")
export TABLESPACE=$(echo $TABLESPACE_SPACEUSED | awk -F", " {'print$1'} | xargs echo)
export SPACEUSED=$(echo $TABLESPACE_SPACEUSED |awk -F", " {'print$2'} | xargs echo)


if [ $TABLESPACE = $TABLESPACE_NAME ] ; then
export ZBX_TABLESPACE=$TABLESPACE
export ZBX_SPACEUSED=$SPACEUSED
else
export SPACEUSED=99
export TABLESPACE=ALGO_DEU_ERRADO
fi

#echo $TABLESPACE_FREE_SIZE > $EXTERNAL_SCRIPT/json_trap
sleep 2
}

discovery_lld(){
$SCRIPT_HOME/oracle_json.py --address ${HOSTNAME} --database ${DATABASE} --port ${PORT} --username ${USER} --password ${PASSWORD} ${MODULE}   > $EXTERNAL_SCRIPT/json_discovery
}


# check exist $SCRIPT_HOME/JSON_TNS/$HOST_ZABBIX.json
if ! [ -e $SCRIPT_HOME/JSON_TNS/$HOST_ZABBIX.json ] ; then
echo $SCRIPT_HOME/JSON_TNS/$HOST_ZABBIX.json "nao existe!"
exit
fi



case $OPERATION in
-t|--trap|trap) 
export TABLESPACE_NAME=$(echo $3 | tr '[:lower:]' '[:upper:]')
zbtrap
;;

-d|--discovery|discovery) 
export MODULE=$(echo $3 | tr '[:upper:]' '[:lower:]')
echo $MODULE >> /tmp/teste
discovery_lld
;;
--create-connection) 
echo "3" 
;;
--check-connection) 
echo "4" 
;;

*) echo "Opcao Invalida!" ;;

esac



