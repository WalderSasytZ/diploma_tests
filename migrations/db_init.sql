DROP TABLE IF EXISTS Q_M;
DROP TABLE IF EXISTS Q_global;
DROP TABLE IF EXISTS Q_user_id;
DROP TABLE IF EXISTS results;

CREATE TABLE IF NOT EXISTS Q_M (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived     TIMESTAMP  NOT NULL,
    algorithm   INT        NOT NULL
);

CREATE TABLE IF NOT EXISTS Q_global (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    sent        TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS Q_user_id (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    sent        TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS results (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived     TIMESTAMP  NOT NULL,
    sent        TIMESTAMP  NOT NULL,
    algorithm   INT        NOT NULL
);