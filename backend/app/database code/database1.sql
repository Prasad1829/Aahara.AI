-- WARNING: this deletes existing ingredient_recipe_ai database
SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;
-- DROP DATABASE IF EXISTS ingredient_recipe_ai;
DROP DATABASE IF EXISTS ingredient_recipe;
CREATE DATABASE ingredient_recipe
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE ingredient_recipe;



-- USERS
CREATE TABLE users (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(190) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_login_at TIMESTAMP NULL DEFAULT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- SAVED RECIPES
CREATE TABLE saved_recipes (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NOT NULL,
    recipe_name VARCHAR(255) NOT NULL,
    ingredients LONGTEXT NULL,
    source_recipe_id INT NULL,
    tried TINYINT(1) NOT NULL DEFAULT 0,
    is_favorite TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_saved_recipes_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- AUDIT LOGS
CREATE TABLE audit_logs (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NULL,
    event_type VARCHAR(80) NOT NULL,
    event_payload LONGTEXT NULL,
    ip_address VARCHAR(64) NULL,
    user_agent VARCHAR(255) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE detection_history (
    id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNSIGNED NULL,
    detected_ingredients LONGTEXT NULL,
    typed_ingredients LONGTEXT NULL,
    recommended_recipe_ids LONGTEXT NULL,
    selected_recipe_id INT NULL,
    `timestamp` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detection_history_user
      FOREIGN KEY (user_id) REFERENCES users(id)
      ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- INDEXES
CREATE INDEX idx_users_role_status ON users(role, status);
CREATE INDEX idx_users_last_login ON users(last_login_at);

CREATE INDEX idx_saved_recipes_user_id ON saved_recipes(user_id);
CREATE INDEX idx_saved_recipes_created_at ON saved_recipes(created_at);
CREATE INDEX idx_saved_recipes_source_recipe_id ON saved_recipes(source_recipe_id);
CREATE INDEX idx_saved_recipes_user_favorite ON saved_recipes(user_id, is_favorite);
CREATE INDEX idx_saved_recipes_user_tried ON saved_recipes(user_id, tried);

CREATE INDEX idx_audit_logs_event_type ON audit_logs(event_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_detection_history_user_id ON detection_history(user_id);
CREATE INDEX idx_detection_history_timestamp ON detection_history(`timestamp`);
CREATE INDEX idx_detection_history_selected_recipe ON detection_history(selected_recipe_id);

-- Prevent duplicate save of same source recipe by same user
ALTER TABLE saved_recipes
  ADD CONSTRAINT uq_saved_recipe_per_user UNIQUE (user_id, source_recipe_id);

SET FOREIGN_KEY_CHECKS = 1;

-- OPTIONAL: make your owner account super admin
-- Change email if needed
UPDATE users
SET role = 'super_admin', status = 'active'
WHERE email = 'swapnilpanchal935@gmail.com';

INSERT INTO users (name, email, password, role, status)
VALUES ('Owner Admin', 'swapnilpanchal935@gmail.com', 'Admin@123', 'super_admin', 'active')
ON DUPLICATE KEY UPDATE
  password = VALUES(password),
  role = 'super_admin',
  status = 'active';
  
  select * from users;



