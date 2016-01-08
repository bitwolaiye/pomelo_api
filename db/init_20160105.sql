CREATE TABLE users
(
  user_id     SERIAL   NOT NULL,
  user_name   TEXT,
  user_avatar TEXT,
  user_gender SMALLINT NOT NULL DEFAULT 0,
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
  PRIMARY KEY (piece_id)
);

CREATE TABLE likes
(
  like_id   SERIAL    NOT NULL,
  like_time TIMESTAMP NOT NULL,
  user_id   INTEGER   NOT NULL REFERENCES users ON DELETE CASCADE,
  piece_id  INTEGER   NOT NULL REFERENCES pieces ON DELETE CASCADE,
  PRIMARY KEY (like_id)
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
  PRIMARY KEY (comment_id)
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
  device_id    SERIAL  NOT NULL,
  device_token TEXT,
  user_id      INTEGER NOT NULL REFERENCES users ON DELETE CASCADE,
  PRIMARY KEY (device_id)
);