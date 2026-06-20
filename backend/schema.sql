CREATE DATABASE IF NOT EXISTS alterme CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE alterme;

CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    avatar_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alter_egos (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    image_url VARCHAR(500) NOT NULL,
    selfie_url VARCHAR(500) NOT NULL,
    universe VARCHAR(50) NOT NULL,
    traits JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alter_ego_styles (
    alter_ego_id VARCHAR(36) NOT NULL,
    style_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (alter_ego_id, style_name),
    FOREIGN KEY (alter_ego_id) REFERENCES alter_egos(id) ON DELETE CASCADE
);
