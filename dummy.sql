INSERT INTO players 
(first_name, last_name, username, email, password, date_of_birth, personal_balance)
VALUES
('Alice', 'Rahman', 'alice_r', 'alice@example.com', 'hashed_pw_1', '2000-05-10', 300.00),
('Bob', 'Khan', 'bob_k', 'bob@example.com', 'hashed_pw_2', '1999-08-22', 250.00),
('Charlie', 'Islam', 'charlie_i', 'charlie@example.com', 'hashed_pw_3', '2001-01-15', 200.00);
INSERT INTO friend_requests (sender_id, receiver_id)
VALUES
(2, 3),
(3, 4);
INSERT INTO friendships (befriender_id, befriended_id)
VALUES
(2, 4);
INSERT INTO game_sessions 
(game_id, player_id, session_no, session_start_time, session_end_time, score)
VALUES
(1, 2, 1, '2025-01-01 10:00:00', '2025-01-01 10:30:00', 1200),
(1, 2, 2, '2025-01-02 11:00:00', '2025-01-02 11:45:00', 1500),
(2, 3, 1, '2025-01-03 09:00:00', '2025-01-03 09:20:00', 1),
(3, 4, 1, '2025-01-04 18:00:00', NULL, 3);
INSERT INTO bank_accounts (account_no, account_type, account_balance)
VALUES
('MONEYGAME-LIME-00002', 'Lime', 1000.00),
('MONEYGAME-BLUE-00003', 'Blue', 800.00),
('MONEYGAME-PINK-00004', 'Pink', 1200.00);
INSERT INTO ownership (player_id, account_no)
VALUES
(2, 'MONEYGAME-LIME-00002'),
(3, 'MONEYGAME-BLUE-00003'),
(4, 'MONEYGAME-PINK-00004');
INSERT INTO transactions 
(sender_account, receiver_account, memo, transaction_amount)
VALUES
('MONEYGAME-LIME-00002', 'MONEYGAME-BLUE-00003', 'Gift', 150.00),
('MONEYGAME-BLUE-00003', 'MONEYGAME-PINK-00004', 'Bribe', 200.00);
INSERT INTO investments 
(player_id, stock_id, investment_amount)
VALUES
(2, 1, 10),
(3, 2, 5),
(4, 3, 8);