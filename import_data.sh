#!/usr/bin/sh
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/channel.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_meta.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question_options.sql
sudo docker exec -i $SQL_SERVER_HOST sh -c "exec mysql -uroot -p$DB_PASSWORD --default-character-set=utf8mb4" < ./sql/data/question.sql
