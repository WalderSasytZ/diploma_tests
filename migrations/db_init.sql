DROP TABLE IF EXISTS Q_M_1;
DROP TABLE IF EXISTS Q_M_2;
DROP TABLE IF EXISTS Q_global;
DROP TABLE IF EXISTS Q_user_id;
DROP TABLE IF EXISTS A1_results;
DROP TABLE IF EXISTS A2_results;

CREATE TABLE IF NOT EXISTS Q_M_1 (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived  TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS Q_M_2 (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived  TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS Q_global (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    sent     TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS Q_user_id (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    sent     TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS A1_results (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived  TIMESTAMP  NOT NULL,
    sent     TIMESTAMP  NOT NULL
);

CREATE TABLE IF NOT EXISTS A2_results (
    message_id  INT        NOT NULL,
    user_id     INT        NOT NULL,
    arrived  TIMESTAMP  NOT NULL,
    sent     TIMESTAMP  NOT NULL
);