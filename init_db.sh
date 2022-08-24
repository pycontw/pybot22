#!/usr/bin/env bash
source ./env.test
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/create_db.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/answer_event.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/channel.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/command_event.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/profile.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question_meta.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question_options.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/question.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/reaction_event.sql

