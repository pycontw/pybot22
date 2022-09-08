#!/usr/bin/env bash

SCRIPT_PATH=$(cd "$( dirname "$0")"; pwd -P)
source $SCRIPT_PATH/../env.var

SQL_SERVER_HOST=$(docker-compose ps -q db)
echo "Create database & tables.. on $SQL_SERVER_HOST"

docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/init_db.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/answer_event.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/channel.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/command_event.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/profile.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question_meta.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question_options.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/reaction_event.sql

# Import data
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/channel.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_meta.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_options.sql
docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question.sql
