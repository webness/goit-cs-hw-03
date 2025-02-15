-- Створення таблиці users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    fullname VARCHAR(100),
    email VARCHAR(100) UNIQUE
);

-- Створення таблиці status
CREATE TABLE status (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

-- Опціонально: заповнення таблиці status базовими значеннями
INSERT INTO status (name) VALUES
    ('new'),
    ('in progress'),
    ('completed');

-- Створення таблиці tasks з зовнішніми ключами
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100),
    description TEXT,
    status_id INTEGER REFERENCES status(id),
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);
