#!/usr/bin/sh

. ./env.test

# pycat bot server
# Build pybot image
sudo docker build -t pycat .
# Run the pybot server
sudo docker run --network my-network -v "$PWD":/pybot22 --env-file=./env.test -d --name pycat-bot pycat

echo "1. pycat running in background, you can enter the docker by\n"
echo "  $ sudo docker exec -it pycat-bot /bin/bash\n"
echo "2. if you would like to run interactive mode, you can background, you can\n"
echo "  $ sudo docker stop pycat-bot\n"
echo "  $ sudo docker run -it --network my-network -v "$PWD":/pybot22 --env-file=./env.test pycat /bin/bash"

# sudo docker run -it --network my-network -v "$PWD":/pybot22 --env-file=./env.test pycat /bin/bash

# sudo docker exec -it pycat-bot /bin/bash
# sudo docker commit -m "your comment" <container_id> <repository:tag>