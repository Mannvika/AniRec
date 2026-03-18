-- AniRec Sample Data Insertion Script
-- This script inserts sample data to test the database structure

-- Insert sample users
INSERT INTO anime_data.users (username, firebase_uid) VALUES 
('testuser1', 'firebase_uid_12345'),
('testuser2', 'firebase_uid_67890'),
('animefan', 'firebase_uid_11111')
ON CONFLICT (username) DO NOTHING;

-- Insert sample anime data
INSERT INTO anime_data.anime (mal_id, title, synopsis, score, popularity, genres, themes, demographics, studios, producers, content_string) VALUES 
(1, 'Cowboy Bebop', 'A space-western anime following the adventures of a group of bounty hunters.', 8.8, 1, ARRAY['Action', 'Sci-Fi'], ARRAY['Space'], ARRAY['Shounen'], ARRAY['Sunrise'], ARRAY['Bandai Visual'], 'Action Sci-Fi Space A space-western anime following the adventures of a group of bounty hunters.'),
(5, 'Cowboy Bebop: The Movie', 'A feature film continuation of the Cowboy Bebop series.', 8.3, 50, ARRAY['Action', 'Sci-Fi'], ARRAY['Space'], ARRAY['Shounen'], ARRAY['Sunrise'], ARRAY['Bandai Visual'], 'Action Sci-Fi Space A feature film continuation of the Cowboy Bebop series.'),
(21, 'One Piece', 'Follows Monkey D. Luffy and his pirate crew in search of the ultimate treasure.', 8.7, 2, ARRAY['Action', 'Adventure', 'Comedy'], ARRAY['Pirates'], ARRAY['Shounen'], ARRAY['Toei Animation'], ARRAY['Fuji TV'], 'Action Adventure Comedy Pirates Follows Monkey D. Luffy and his pirate crew in search of the ultimate treasure.'),
(30, 'Neon Genesis Evangelion', 'Teenage pilots control giant mechs to save humanity from mysterious angels.', 8.2, 10, ARRAY['Action', 'Drama', 'Mecha'], ARRAY['Military', 'Psychological'], ARRAY['Shounen'], ARRAY['Gainax', 'Studio Khara'], ARRAY['TV Tokyo'], 'Action Drama Mecha Military Psychological Teenage pilots control giant mechs to save humanity from mysterious angels.')
ON CONFLICT (mal_id) DO NOTHING;

-- Insert sample ratings
INSERT INTO anime_data.user_ratings (user_id, anime_id, score) VALUES 
(1, 1, 10),
(1, 21, 9),
(1, 30, 8),
(2, 1, 9),
(2, 5, 8),
(2, 21, 10),
(3, 30, 9),
(3, 1, 7),
(3, 21, 8)
ON CONFLICT (user_id, anime_id) DO NOTHING;

-- Verify data insertion
SELECT 'Users:' as table_name, COUNT(*) as record_count FROM anime_data.users
UNION ALL
SELECT 'Anime:', COUNT(*) FROM anime_data.anime
UNION ALL
SELECT 'User Ratings:', COUNT(*) FROM anime_data.user_ratings;
