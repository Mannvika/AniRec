import psycopg2
import time
from jikanpy import Jikan

def load_password():
    with open('password', 'r') as file:
        password = file.read().strip()
    return password

password = load_password()

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname='AniRec',
            user='postgres',
            password=password,
            host='localhost',
            port='5432'
        )
        print("Database connection established successfully.")
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

def fetch_and_insert_anime_data(connection):
    jikan = Jikan()
    cursor = connection.cursor()
    
    print("Starting data fetch from Jikan API...")
    try:
        for i in range(1, 101): 
            print(f"Fetching page {i}...")
            response = jikan.top(type='anime', page=i)
            anime_list = response.get('data', [])

            time.sleep(1.1)

            for anime in anime_list:
                mal_id = anime.get('mal_id')
                title = anime.get('title')
                synopsis = anime.get('synopsis')
                score = anime.get('score')
                popularity = anime.get('popularity')
                genres = [genre['name'] for genre in anime.get('genres', [])]
                themes = [theme['name'] for theme in anime.get('themes', [])]
                demographics = [demo['name'] for demo in anime.get('demographics', [])]
                studios = [studio['name'] for studio in anime.get('studios', [])]
                producers = [producer['name'] for producer in anime.get('producers', [])]

                if not mal_id:
                    continue

                cursor.execute("""
                    INSERT INTO anime_data.anime (mal_id, title, synopsis, score, popularity, genres, themes, demographics, studios, producers)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (mal_id) DO NOTHING;
                """, (mal_id, title, synopsis, score, popularity, genres, themes, demographics, studios, producers))
        
        connection.commit()
        print("Data insertion complete and committed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")
        connection.rollback()
    finally:
        cursor.close()

    
def close_connection(connection):
    if connection:
        try:
            connection.close()
            print("Database connection closed.")
        except psycopg2.Error as e:
            print(f"Error closing the database connection: {e}")
    else:
        print("No connection to close.")

if __name__ == "__main__":
    db_connection = connect_to_db()
    if db_connection:
        fetch_and_insert_anime_data(db_connection)
        close_connection(db_connection)
    else:
        print("Failed to connect to the database.")