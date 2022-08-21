#!/usr/bin/sh
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/data/channel.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/data/question_meta.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/data/question_options.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD" < ./sql/data/question.sql
