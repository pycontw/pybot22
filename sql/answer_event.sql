USE pycon22;

CREATE TABLE `answer_event` (
    `event_id` VARCHAR(26) NOT NULL PRIMARY KEY,
    `uid` VARCHAR(32) NOT NULL,
    `question_id` VARCHAR(64) NOT NULL,
    `received_answer` TEXT,
    `is_correct` BOOLEAN DEFAULT 0,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    INDEX uid_qid (`uid`, `question_id`)
);
