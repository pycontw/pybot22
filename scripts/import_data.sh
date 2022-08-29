#!/usr/bin/env bash
SCRIPT_PATH=$(cd "$( dirname "$0")"; pwd -P)
source $SCRIPT_PATH/../env.test

echo "Import data from sql files to $SQL_SERVER_HOST"

sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/channel.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_meta.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_options.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question.sql
