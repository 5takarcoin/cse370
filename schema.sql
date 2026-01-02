CREATE TABLE players (
        player_id INT PRIMARY KEY AUTO_INCREMENT,
        first_name VARCHAR(25) NOT NULL,
        last_name VARCHAR(25) NOT NULL,
        username VARCHAR(30) NOT NULL UNIQUE,
        email VARCHAR(255) NOT NULL UNIQUE,
        password CHAR(60) NOT NULL,
        date_of_birth DATE NOT NULL,
        personal_balance DECIMAL(10,2) NOT NULL DEFAULT 500.00
);

CREATE TABLE friend_requests(
        sender_id INT NOT NULL,
        receiver_id INT NOT NULL,
        frq_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (sender_id, receiver_id),
        FOREIGN KEY (sender_id) REFERENCES players(player_id),
        FOREIGN KEY (receiver_id) REFERENCES players(player_id)
);

CREATE TABLE friendships(
        befriender_id INT NOT NULL,
        befriended_id INT NOT NULL,
        frn_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (befriender_id, befriended_id),
        FOREIGN KEY (befriender_id) REFERENCES players(player_id),
        FOREIGN KEY (befriended_id) REFERENCES players(player_id)
);

CREATE TABLE games (
        game_id INT PRIMARY KEY AUTO_INCREMENT,
        game_name VARCHAR(60) NOT NULL
);

CREATE TABLE game_genres (
        game_id INT NOT NULL,
        game_genre VARCHAR(60) NOT NULL,
        PRIMARY KEY (game_id, game_genre),
        FOREIGN KEY (game_id) REFERENCES games(game_id)
);

CREATE TABLE game_sessions (
        game_id INT NOT NULL,
        player_id INT NOT NULL,
        session_no INT NOT NULL,
        session_start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        session_end_time DATETIME NULL,
        score INT NOT NULL,
        PRIMARY KEY (game_id, player_id, session_no),
        FOREIGN KEY (game_id) REFERENCES games(game_id),
        FOREIGN KEY (player_id) REFERENCES players(player_id)
);

CREATE TABLE bank_accounts (
    account_no VARCHAR(100) PRIMARY KEY,
    account_type CHAR(4) NOT NULL,
    account_balance DECIMAL(10, 2)
);

CREATE TABLE ownership (
    player_id INT NOT NULL,
    account_no VARCHAR(100) NOT NULL,
    FOREIGN KEY (player_id) REFERENCES players(player_id),
    FOREIGN KEY (account_no) REFERENCES bank_accounts(account_no),
    PRIMARY KEY(player_id, account_no)
);

CREATE TABLE transactions (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    sender_account VARCHAR(100) NOT NULL,
    receiver_account VARCHAR(100) NOT NULL,
    transaction_amount DECIMAL(10,2) NOT NULL,
    memo VARCHAR(255),
    transaction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_account) REFERENCES bank_accounts(account_no),
    FOREIGN KEY (receiver_account) REFERENCES bank_accounts(account_no)
);

CREATE TABLE stocks (
        stock_id INT PRIMARY KEY AUTO_INCREMENT,
        abbreviation CHAR(3) NOT NULL,
        exchange CHAR(4) NOT NULL,
        UNIQUE (abbreviation, exchange)
);

CREATE TABLE investments (
        player_id INT,
        stock_id INT,
        investment_date DATETIME(0) DEFAULT CURRENT_TIMESTAMP,
        investment_amount INT NOT NULL,
        FOREIGN KEY (player_id) REFERENCES players(player_id),
        FOREIGN KEY (stock_id) REFERENCES stocks(stock_id),
        PRIMARY KEY(player_id, stock_id, investment_date)
);

