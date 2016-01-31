CREATE TABLE users
(
  user_id       SERIAL   NOT NULL,
  user_name     TEXT     NOT NULL,
  nick_name     TEXT     NOT NULL,
  user_avatar   TEXT,
  user_gender   SMALLINT NOT NULL DEFAULT 0,
  user_password TEXT     NOT NULL,
  PRIMARY KEY (user_id)
);

CREATE TABLE channels
(
  channel_id      SERIAL  NOT NULL,
  channel_name    TEXT,
  channel_avatar  TEXT,
  channel_user_id INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
  PRIMARY KEY (channel_id)
);

CREATE TABLE pieces
(
  piece_id    SERIAL    NOT NULL,
  piece_pic   TEXT,
  piece_text  TEXT,
  piece_voice TEXT,
  piece_video TEXT,
  piece_time  TIMESTAMP NOT NULL,
  user_id     INTEGER   NOT NULL REFERENCES users ON DELETE CASCADE,
  channel_id  INTEGER   NOT NULL REFERENCES channels ON DELETE CASCADE,
  like_cnt    INTEGER   NOT NULL DEFAULT 0,
  comment_cnt INTEGER   NOT NULL DEFAULT 0,
  PRIMARY KEY (piece_id)
);

CREATE TABLE piece_likes
(
  piece_id INTEGER NOT NULL REFERENCES pieces ON DELETE CASCADE,
  user_id  INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
  status   INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (piece_id, user_id)
);

CREATE TABLE comments
(
  comment_id    SERIAL    NOT NULL,
  comment_pic   TEXT,
  comment_text  TEXT,
  comment_voice TEXT,
  comment_video TEXT,
  comment_time  TIMESTAMP NOT NULL,
  user_id       INTEGER   NOT NULL REFERENCES users ON DELETE CASCADE,
  piece_id      INTEGER   NOT NULL REFERENCES pieces ON DELETE CASCADE,
  like_cnt      INTEGER   NOT NULL DEFAULT 0,
  PRIMARY KEY (comment_id)
);

CREATE TABLE comment_likes
(
  comment_id INTEGER NOT NULL REFERENCES comments ON DELETE CASCADE,
  user_id    INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
  status     INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (comment_id, user_id)
);

CREATE TABLE messages
(
  message_id   SERIAL    NOT NULL,
  message_json TEXT      NOT NULL,
  message_time TIMESTAMP NOT NULL,
  user_id      INTEGER   NOT NULL REFERENCES users ON DELETE CASCADE,
  PRIMARY KEY (message_id)
);

CREATE TABLE devices
(
  device_id       SERIAL  NOT NULL,
  device_token    TEXT,
  user_id         INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
  last_message_id INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (device_id)
);