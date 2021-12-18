#!/usr/bin/env bash
#docker-compose up db-service -d

sleep 10
#docker-compose up hw2 -d

#docker cp baseball.sql db-service:/baseball.sql
#docker cp HW2.sql db-service:/HW2.sql

#Thanks to Will for help here as well
if ! mysql -h db-service -uroot -psecret -e 'use baseball'; then
  mysql -h db-service -uroot -psecret -e "create database baseball;"
  mysql -h db-service -uroot -psecret -D baseball < /data/baseball.sql
fi

#commented out for testing
mysql -h db-service -uroot -psecret -D baseball < /data/HW2.sql

python HW6.py
