USE pycon22;

CREATE TABLE `command_event` (
    `event_id` VARCHAR(26) NOT NULL PRIMARY KEY,
    `uid` VARCHAR(32) NOT NULL,
    `command` VARCHAR(64) NOT NULL,
    `name` VARCHAR(128) DEFAULT '',
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
