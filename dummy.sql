INSERT INTO players 
(first_name, last_name, username, email, password, date_of_birth, personal_balance)
VALUES
('Alice', 'Rahman', 'alice_r', 'alice@example.com', 'hashed_pw_1', '2000-05-10', 300.00),
('Bob', 'Khan', 'bob_k', 'bob@example.com', 'hashed_pw_2', '1999-08-22', 250.00),
('Charlie', 'Islam', 'charlie_i', 'charlie@example.com', 'hashed_pw_3', '2001-01-15', 200.00);
INSERT INTO friend_requests (sender_id, receiver_id)
VALUES
(1, 2),
(2, 3);
INSERT INTO friendships (befriender_id, befriended_id)
VALUES
(1, 3),
(2, 1);
INSERT INTO games (game_name)
VALUES
('Coin Toss');
('Black Jack'),
('Spin The Wheel'),
('Rock-Paper-Scissors');
INSERT INTO game_genres (game_id, game_genre)
VALUES
(1, 'Arcade'),
(1, 'Shooter'),
(2, 'Strategy'),
(3, 'Sports');
INSERT INTO game_sessions 
(game_id, player_id, session_no, session_start_time, session_end_time, score)
VALUES
(1, 1, 1, '2025-01-01 10:00:00', '2025-01-01 10:30:00', 1200),
(1, 1, 2, '2025-01-02 11:00:00', '2025-01-02 11:45:00', 1500),
(2, 2, 1, '2025-01-03 09:00:00', '2025-01-03 09:20:00', 1),
(3, 3, 1, '2025-01-04 18:00:00', NULL, 3);
INSERT INTO bank_accounts (account_no, account_type, account_balance)
VALUES
('ACC1001', 'SAVING', 1000.00),
('ACC1002', 'HARAM', 800.00),
('ACC1003', 'SAVING', 1200.00);
INSERT INTO ownership (player_id, account_no)
VALUES
(1, 'ACC1001'),
(2, 'ACC1002'),
(3, 'ACC1003');
INSERT INTO transactions 
(sender_account, receiver_account, memo, transaction_amount)
VALUES
('ACC1001', 'ACC1002', 'Game payment', 150.00),
('ACC1002', 'ACC1003', 'Friend transfer', 200.00);
INSERT INTO stocks (abbreviation, exchange)
VALUES
('AAPL', 'NASDAQ'),
('GOOG', 'NASDAQ'),
('TSLA', 'NYSE');
INSERT INTO investments 
(player_id, stock_id, investment_amount)
VALUES
(1, 1, 10),
(2, 2, 5),
(3, 3, 8);
