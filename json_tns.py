#!/usr/bin/env python
# coding: utf-8

import json

#Define string connection (using SQL Server sintax]
str_connection = ('DRIVER={ODBC Driver 17 for SQL Server};SERVER=[tcp:myserver1.database.windows.net,tcp:myserver2.database.windows.net];PORT=1433;DATABASE=mydb;INSTANCE=[INST1,INST2];UID=myusername;PWD=mypassword;SERVICE_NAME=service')

#Extract parameters from string connection
split_connection = str_connection.split(";")


#Extract PORT

port = [element.startswith("PORT") for element in split_connection]
port = [i for (i, v) in zip(split_connection, port) if v]
port_ = port[0][5:]

#Extract DATABASE

database = [element.startswith("DATABASE") for element in split_connection]
database = [i for (i, v) in zip(split_connection, database) if v]
database_ = database[0][9:]

#Extract credencial (UID,PWD)

uid = [element.startswith("UID") for element in split_connection]
uid = [i for (i, v) in zip(split_connection, uid) if v]
uid_ = uid[0][4:]

pwd = [element.startswith("PWD") for element in split_connection]
pwd = [i for (i, v) in zip(split_connection, pwd) if v]
pwd_ = pwd[0][4:]

#Extract Service

service = [element.startswith("SERVICE_NAME") for element in split_connection]
service = [i for (i, v) in zip(split_connection, service) if v]
service_ = service[0][13:]

#Extract server (or hostname)

server = [element.startswith("SERVER") for element in split_connection]
server = [i for (i, v) in zip(split_connection, server) if v]
server_ = [i[7:] for i in server ]
server_ = server_[0].split(",")

#Extract instance
instance = [element.startswith("INSTANCE") for element in split_connection]
instance = [i for (i, v) in zip(split_connection, instance) if v]
instance_ = [i[9:] for i in instance ]
instance_ = instance_[0].split(",") 


#Define variables from parameters extraction
database = database_ ;
credencial = "UID="+uid_+"PWD="+pwd_
service_names = service_
hostname = server_
port = port_
instance = instance_

# Number of servers
size = len(hostname)


#Create dict with Machine's parameters (list is requeriment)
machine = [{"hostname":hostname[i],"port":port,"instance":instance[i]}  for i in range(0,size)]


#Create dict with JSON structure
dct = {"database":database,"credencial":credencial,"service_names":service_names,"MACHINE":machine}

#Save JSON file
with open("test.json", 'w') as f:
    json.dump(dct, f)
