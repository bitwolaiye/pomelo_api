INSERT INTO users(user_id, user_name, user_gender) VALUES (1, 'bitwolaiye', 1);
INSERT INTO users(user_id, user_name, user_gender) VALUES (2, 'bitning', 0);

SELECT setval('users_user_id_seq', 10000);