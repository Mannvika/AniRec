-- AniRec Database Reset Script
-- This script drops all tables and recreates the schema
-- WARNING: This will delete all existing data!

-- Drop all tables in reverse order of dependencies
DROP TABLE IF EXISTS anime_data.user_ratings CASCADE;
DROP TABLE IF EXISTS anime_data.reviews CASCADE;
DROP TABLE IF EXISTS anime_data.anime CASCADE;
DROP TABLE IF EXISTS anime_data.users CASCADE;

-- DROP SCHEMA IF EXISTS anime_data CASCADE;

-- Recreate schema
CREATE SCHEMA IF NOT EXISTS anime_data;

-- Recreate tables
CREATE TABLE anime_data.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL
);

CREATE TABLE anime_data.anime (
    mal_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    synopsis TEXT,
    score FLOAT,
    popularity INTEGER,
    genres TEXT[],
    themes TEXT[],
    demographics TEXT[],
    studios TEXT[],
    producers TEXT[],
    content_string TEXT
);

CREATE TABLE anime_data.user_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    anime_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    CONSTRAINT fk_user_ratings_user 
        FOREIGN KEY(user_id) REFERENCES anime_data.users(id) 
        ON DELETE CASCADE,
    CONSTRAINT fk_user_ratings_anime 
        FOREIGN KEY(anime_id) REFERENCES anime_data.anime(mal_id) 
        ON DELETE CASCADE
);

CREATE TABLE anime_data.reviews (
    review_id INTEGER PRIMARY KEY,
    anime_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    CONSTRAINT fk_reviews_anime 
        FOREIGN KEY(anime_id) REFERENCES anime_data.anime(mal_id) 
        ON DELETE CASCADE
);

-- Create unique constraint
ALTER TABLE anime_data.user_ratings 
ADD CONSTRAINT _user_anime_uc UNIQUE (user_id, anime_id);

-- Create indexes
CREATE INDEX idx_anime_mal_id ON anime_data.anime(mal_id);
CREATE INDEX idx_anime_title ON anime_data.anime USING gin(to_tsvector('english', title));
CREATE INDEX idx_anime_score ON anime_data.anime(score);
CREATE INDEX idx_anime_popularity ON anime_data.anime(popularity);
CREATE INDEX idx_user_ratings_user_id ON anime_data.user_ratings(user_id);
CREATE INDEX idx_user_ratings_anime_id ON anime_data.user_ratings(anime_id);
CREATE INDEX idx_user_ratings_score ON anime_data.user_ratings(score);
CREATE INDEX idx_users_firebase_uid ON anime_data.users(firebase_uid);
CREATE INDEX idx_users_username ON anime_data.users(username);
CREATE INDEX idx_reviews_anime_id ON anime_data.reviews(anime_id);
CREATE INDEX idx_reviews_review_id ON anime_data.reviews(review_id);

-- Reset sequences
ALTER SEQUENCE anime_data.users_id_seq RESTART WITH 1;
ALTER SEQUENCE anime_data.user_ratings_id_seq RESTART WITH 1;
