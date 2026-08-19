USE Millionaire;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS game_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(50),
    difficulty VARCHAR(20),
    score INT,
    played DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS game_results (
    id INT AUTO_INCREMENT PRIMARY KEY,

    session_id INT NOT NULL,
    username VARCHAR(50),
    question TEXT,
    selected_answer TEXT,
    correct_answer TEXT,
    was_correct BOOLEAN,

    FOREIGN KEY (session_id)
        REFERENCES game_sessions(id)
);


CREATE TABLE IF NOT EXISTS topic_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    username VARCHAR(50),
    difficulty VARCHAR(20),
    topic VARCHAR(100),

    UNIQUE(user_id, difficulty, topic),

    FOREIGN KEY (user_id)
        REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS available_topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topic VARCHAR(100) NOT NULL UNIQUE
);

INSERT IGNORE INTO available_topics (topic) VALUES
('Advanced Persistent Threats'),('Asymmetric/Symmetric Encryption for Cryptography'),
('Blockchain Security'),('Cyber Incident Response'),('Cyber Threat Intelligence'),
('Cyberbullying'),('Cryptography'),('Data'),('Digital Footprints'),
('Digital Forensics'),('Encryption'),('Endpoint Security'),('Ethical Hacking'),('Firewall'),
('HTTP Headers'),('Hacking'),('Internet Safety'),('Intrusion Detection Systems'),
('Kerberos Authentication'),('Linux/Unix System Forensics'),('Malware'),('Network Encryption'),
('Network Security'),('Passwords'),('Phishing'),('Safe Downloading'),('Secure Coding Practices'),
('Secure Websites'),('Social Engineering'),('Social Media'),('TCP Protocol'),('TCP/UDP Protocol'),
('Technical Aspects of Network Protocols'),('Two-factor authentication'),('Virtualization'),
('Wireless Security Protocol'),('SSL/X509 Certificates');

DELIMITER //

DROP TRIGGER IF EXISTS game_sessions_set_username//

CREATE TRIGGER game_sessions_set_username
BEFORE INSERT ON game_sessions
FOR EACH ROW
BEGIN
    SET NEW.username = (
        SELECT username
        FROM users
        WHERE id = NEW.user_id
    );
END//

DROP TRIGGER IF EXISTS topic_settings_set_username//

CREATE TRIGGER topic_settings_set_username
BEFORE INSERT ON topic_settings
FOR EACH ROW
BEGIN
    SET NEW.username = (
        SELECT username
        FROM users
        WHERE id = NEW.user_id
    );
END//

DROP TRIGGER IF EXISTS game_results_set_username//

CREATE TRIGGER game_results_set_username
BEFORE INSERT ON game_results
FOR EACH ROW
BEGIN
    SET NEW.username = (
        SELECT username
        FROM game_sessions
        WHERE id = NEW.session_id
    );
END//

DELIMITER ;