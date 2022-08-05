USE pycon22;

CREATE TABLE `question` (
    `qid` VARCHAR(32) NOT NULL,
    `lang` VARCHAR(16) NOT NULL,
    `description` VARCHAR(1024) NOT NULL,
    `answer` VARCHAR(1024) NOT NULL,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`qid`, `lang`)
);
