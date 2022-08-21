#!/usr/bin/sh
# Construct a network
sudo docker network create -d bridge my-network

# MYSQL server
# Pull mysql image from Docker Hub
sudo docker pull mysql
# Run the mysql container
# docker run -p 6606:3306 -d --name mysql-server --network my-network -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" mysql:5.7

mkdir db_data

sudo docker run -p 3306:3306 -d --name mysql-server --network my-network -v $PWD/db_data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD="$DB_PASSWORD" mysql

. ./env.test
. ./init_db.sh
. ./import_data.sh

# Enter Mysql for test
# sudo docker run -it --rm --network my-network mysql:5.7 sh -c 'exec mysql -h"mysql-server" -P"3306" -uroot -p"$DB_PASSWORD"'
# sudo docker exec -i mysql-server sh -c "exec mysql -uroot -p$DB_PASSWORD" < /some/path/on/your/host/all-databases.sql

# pycat bot server
# Build pybot image
sudo docker build -t pycat .
# Run the pybot server
# sudo docker run --network my-network -v "$PWD":/pybot22 -d pycat

sudo docker run -it --network my-network -v "$PWD":/pybot22 --env-file=./env.test pycat /bin/bash

# docker exec -it pycat /bin/bash
# docker commit -m "your comment" <container_id> <repository:tag>