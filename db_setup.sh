#!/usr/bin/sh
# Construct a network
sudo docker network create -d bridge my-network

# MYSQL server
# Pull mysql image from Docker Hub
sudo docker pull mysql
# Run the mysql container
# docker run -p 6606:3306 -d --name mysql-server --network my-network -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" mysql:5.7

mkdir db_data

. ./env.test

sudo docker run -p 3306:3306 -d --name mysql-server --network my-network -v $PWD/db_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" mysql

until nc -z localhost 3307; do sleep 1; echo "Waiting for DB to come up..."; done

. ./init_db.sh
. ./import_data.sh

# Enter Mysql for test
# sudo docker run -it --rm --network my-network mysql:5.7 sh -c 'exec mysql -h"mysql-server" -P"3306" -uroot -p"$DB_PASSWORD"'
# sudo docker exec -i mysql-server sh -c "exec mysql -uroot -p$DB_PASSWORD" < /some/path/on/your/host/all-databases.sql
