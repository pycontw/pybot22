USE pycon22;

CREATE TABLE `question` (
    `qid` VARCHAR(32) NOT NULL,
    `lang` VARCHAR(16) NOT NULL,
    `description` VARCHAR(1024) NOT NULL,
    `answer` VARCHAR(1024) NOT NULL,
    `coin` SMALLINT UNSIGNED DEFAULT 0,
    `star` SMALLINT UNSIGNED DEFAULT 0,
    `q_type` VARCHAR(16) NOT NULL,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`qid`, `lang`)
);
