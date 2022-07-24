USE pycon22;

CREATE TABLE `reaction_event` (
    `event_id` VARCHAR(26) NOT NULL PRIMARY KEY,
    `uid` VARCHAR(32) NOT NULL,
    `qid` VARCHAR(64) NOT NULL,
    `channel_id` VARCHAR(64) NOT NULL,
    `channel_name` VARCHAR(64) NOT NULL,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX uid_qid (`uid`, `question_id`)
);
