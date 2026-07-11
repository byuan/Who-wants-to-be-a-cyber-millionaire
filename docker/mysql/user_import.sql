USE Millionaire;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    difficulty VARCHAR(20),
    score INT,
    played DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS game_results (
    id INT AUTO_INCREMENT PRIMARY KEY,

    session_id INT NOT NULL,

    question TEXT,
    chosen_answer INT,
    correct_answer INT,
    was_correct BOOLEAN,

    FOREIGN KEY (session_id)
        REFERENCES game_sessions(id)
);


CREATE TABLE IF NOT EXISTS topic_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    difficulty VARCHAR(20),
    topic VARCHAR(100),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);