REPLACE INTO `pycon22`.`channel` (`channel_id`,`channel_name`,`welcome_msg`,`created`) VALUES ('1003242909950292058','test-answer','歡迎來到大地遊戲贊助商關卡。請點選表情符號以選擇要回答的題目，點擊之後你將會收到來自 PyBot22 的私訊，請在與機器人的私訊中回答問題。
可能的答案們：Unknown, Hello, XM5 good, 哈哈, 超棒, 未知','2022-08-07 11:15:15');
REPLACE INTO `pycon22`.`question_meta` (`qid`,`emoji`,`coin`,`star`,`q_type`,`channel_id`,`created`) VALUES ('micron_q1','🐱','2000','1','option_only','1003242909950292058','2022-08-05 23:46:34');
REPLACE INTO `pycon22`.`question_meta` (`qid`,`emoji`,`coin`,`star`,`q_type`,`channel_id`,`created`) VALUES ('micron_q2','😘','0','0','pure_message','1003242909950292058','2022-08-08 20:31:33');
REPLACE INTO `pycon22`.`question_meta` (`qid`,`emoji`,`coin`,`star`,`q_type`,`channel_id`,`created`) VALUES ('u_qa_01','💰','100','0','questionare','1003242909950292058','2022-08-18 20:19:51');
REPLACE INTO `pycon22`.`question_meta` (`qid`,`emoji`,`coin`,`star`,`q_type`,`channel_id`,`created`) VALUES ('u_qa_02','💰','100','0','questionare','1003242909950292058','2022-08-18 20:19:51');
UPDATE `pycon22`.`profile` SET `is_staff` = '1' WHERE (`uid` = '666602479433154570');