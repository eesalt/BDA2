#!/usr/bin/env bash
docker-compose up hw2 -d
docker-compose up db-service -d
docker cp baseball.sql db-service:/baseball.sql
docker cp HW2.sql db-service:/HW2.sql

#Thanks to Will for help here as well
if ! docker container exec -i db-service mysql -uroot -psecret -e'use baseball';
then
  docker container exec -i db-service mysql -uroot -psecret -e'create database baseball';
  docker container exec -i db-service mysql baseball < baseball.sql -psecret
fi
  docker container exec -i db-service mysql -uroot -psecret -e'use baseball';
  docker container exec -i db-service mysql baseball < HW2.sql -psecret


