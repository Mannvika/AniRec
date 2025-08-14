import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import psycopg2
import time
from jikanpy import Jikan
from database.db_helper import connect_to_db, close_connection

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

def fetch_and_insert_review_data(connection):
    """
    Fetches anime reviews from the Jikan API and inserts them into a database.

    This updated function uses the jikan.anime(id, 'reviews') endpoint and includes
    more robust rate limiting to prevent API errors.
    """
    jikan = Jikan()
    cursor = connection.cursor()
    
    print("Starting review data fetch from Jikan API...")
    try:
        for i in range(1, 101): 
            print(f"Fetching top anime list: page {i}...")
            response = jikan.top(type='anime', page=i)
            anime_list = response.get('data', [])
            time.sleep(1.1)
            for anime in anime_list:
                mal_id = anime.get('mal_id')
                if not mal_id:
                    continue
                print(f"  Fetching reviews for anime ID: {mal_id}...")
                try:
                    reviews_response = jikan.anime(mal_id, 'reviews')
                    reviews = reviews_response.get('data', [])
                    
                    time.sleep(0.5) 
                    for review in reviews:
                        review_id = review.get('mal_id')
                        review_text = review.get('review')
                        if not review_id or not review_text:
                            continue
                        cursor.execute("""
                            INSERT INTO anime_data.reviews (review_id, anime_id, review_text)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (review_id) DO NOTHING;
                        """, (review_id, mal_id, review_text))
                
                except Exception as review_error:
                    print(f"    Could not fetch reviews for anime ID {mal_id}: {review_error}")
                    time.sleep(1)
        connection.commit()
        print("\nReview data insertion complete and committed successfully.")

    except Exception as e:
        print(f"\nAn error occurred during the process: {e}")
        print("Rolling back any uncommitted changes.")
        connection.rollback()
    finally:
        print("Closing the database cursor.")
        cursor.close()

if __name__ == "__main__":
    db_connection = connect_to_db()

    if db_connection:
        fetch_and_insert_anime_data(db_connection)
        fetch_and_insert_review_data(db_connection)
        close_connection(db_connection)
    else:
        print("Failed to connect to the database.")