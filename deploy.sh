#!/usr/bin/env bash

# Construct a network
sudo docker network create -d bridge my-network

# setup db and import data sets
scripts/db_setup.sh

source ./env.test

# pycat bot server
# Build pybot image
sudo docker build -t pycat .
# Run the pybot server
sudo docker run --network my-network -v "$PWD":/pybot22 --env-file=./env.test -d --name pycat-bot pycat

echo "1. pycat running in background, you can enter the docker by"
echo "  $ sudo docker exec -it pycat-bot /bin/bash"
echo "2. if you would like to run in interactive mode, you can"
echo "  $ sudo docker stop pycat-bot"
echo "  $ sudo docker run -it --network my-network -v "$PWD":/pybot22 --env-file=./env.test pycat /bin/bash"
