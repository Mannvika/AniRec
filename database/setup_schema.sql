-- AniRec Database Schema Setup

-- CREATE DATABASE AniRec;

-- Create the schema
CREATE SCHEMA IF NOT EXISTS anime_data;

-- Create the users table
CREATE TABLE IF NOT EXISTS anime_data.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    firebase_uid VARCHAR(128) UNIQUE NOT NULL
);

-- Create the anime table
CREATE TABLE IF NOT EXISTS anime_data.anime (
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

-- Create the user_ratings table
CREATE TABLE IF NOT EXISTS anime_data.user_ratings (
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

-- Create the reviews table
CREATE TABLE IF NOT EXISTS anime_data.reviews (
    review_id INTEGER PRIMARY KEY,
    anime_id INTEGER NOT NULL,
    review_text TEXT NOT NULL,
    CONSTRAINT fk_reviews_anime 
        FOREIGN KEY(anime_id) REFERENCES anime_data.anime(mal_id) 
        ON DELETE CASCADE
);

-- Create unique constraint for user-anime rating combination
ALTER TABLE anime_data.user_ratings 
ADD CONSTRAINT _user_anime_uc UNIQUE (user_id, anime_id);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_anime_mal_id ON anime_data.anime(mal_id);
CREATE INDEX IF NOT EXISTS idx_anime_title ON anime_data.anime USING gin(to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_anime_score ON anime_data.anime(score);
CREATE INDEX IF NOT EXISTS idx_anime_popularity ON anime_data.anime(popularity);
CREATE INDEX IF NOT EXISTS idx_user_ratings_user_id ON anime_data.user_ratings(user_id);
CREATE INDEX IF NOT EXISTS idx_user_ratings_anime_id ON anime_data.user_ratings(anime_id);
CREATE INDEX IF NOT EXISTS idx_user_ratings_score ON anime_data.user_ratings(score);
CREATE INDEX IF NOT EXISTS idx_users_firebase_uid ON anime_data.users(firebase_uid);
CREATE INDEX IF NOT EXISTS idx_users_username ON anime_data.users(username);
CREATE INDEX IF NOT EXISTS idx_reviews_anime_id ON anime_data.reviews(anime_id);
CREATE INDEX IF NOT EXISTS idx_reviews_review_id ON anime_data.reviews(review_id);

-- Grant permissions (adjust username as needed)
-- GRANT ALL PRIVILEGES ON SCHEMA anime_data TO postgres;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA anime_data TO postgres;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA anime_data TO postgres;
