USE pycon22;

CREATE TABLE `question_options` (
    `qid` VARCHAR(32) NOT NULL,
    `lang` VARCHAR(16) NOT NULL,
    `options` JSON NOT NULL,
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (`qid`, `option_id`, `lang`)
);
