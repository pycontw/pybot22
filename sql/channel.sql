USE pycon22;

CREATE TABLE `channel` (
    `channel_id` VARCHAR(19) PRIMARY KEY,
    `channel_name` VARCHAR(32) DEFAULT '',
    `welcome_msg` VARCHAR(2000) DEFAULT '',
    `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
