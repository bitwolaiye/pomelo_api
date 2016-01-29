INSERT INTO users(user_id, user_name, user_gender) VALUES (1, 'bitwolaiye', 1);
INSERT INTO users(user_id, user_name, user_gender) VALUES (2, 'bitning', 0);

INSERT INTO users(user_id, user_name, user_gender) VALUES (9, '柚小秘', 0);

SELECT setval('users_user_id_seq', 10000);

INSERT INTO channels(channel_id, channel_name, channel_avatar, channel_user_id) VALUES (1, '今天是个大晴天', 'pomelo_1' ,1);
INSERT INTO channels(channel_id, channel_name, channel_avatar, channel_user_id) VALUES (2, '我就爱自拍', 'pomelo_2' ,2);

SELECT setval('channels_channel_id_seq', 10000);