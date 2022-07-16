USE pycon22;

CREATE TABLE `answer_event` (
    `event_id` VARCHAR(26) NOT NULL PRIMARY KEY,
    `uid` VARCHAR(32) NOT NULL,
    `question_id` VARCHAR(64) NOT NULL,
    `received_answer` TEXT,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
