#!/usr/bin/env bash

# MYSQL server
# Pull mysql image from Docker Hub
sudo docker pull mysql
# Run the mysql container

# create a local space to store the database raw file
mkdir db_data

SCRIPT_PATH=$(cd "$( dirname "$0")"; pwd -P)

source $SCRIPT_PATH/../env.test

sudo docker run -p 3306:3306 -d --name $SQL_SERVER_HOST --network my-network -v $PWD/db_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" mysql

echo "Connection to MySQL server: $SQL_SERVER_HOST"

until nc -z localhost 3306; do sleep 1; echo "Waiting for DB to come up..."; done

$SCRIPT_PATH/init_db.sh
$SCRIPT_PATH/import_data.sh
