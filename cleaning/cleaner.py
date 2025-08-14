import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pandas as pd
import spacy
from psycopg2.extras import execute_values
from database.db_helper import connect_to_db, close_connection

def load_data_to_dataframe(connection):
    query = "SELECT * FROM anime_data.anime;"
    df = pd.read_sql_query(query, connection)
    return df

def preprocess_anime_data(df):
    print("Preprocessing anime data...")
    nlp = spacy.load("en_core_web_sm", disable=["ner", "parser"])
    
    genres_str = df['genres'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
    themes_str = df['themes'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)

    uncleaned_content = genres_str.fillna('') + ' ' + themes_str.fillna('') + ' ' + df['synopsis'].fillna('')

    cleaned_docs = []
    for doc in nlp.pipe(uncleaned_content, batch_size=100, n_process=-1):
        cleaned_text = ' '.join([token.text for token in doc if not token.is_stop and not token.is_punct])
        cleaned_docs.append(cleaned_text)

    df['content_string'] = cleaned_docs

    print("Preprocessing complete.")
    return df

if __name__ == "__main__":
    if not spacy.util.is_package("en_core_web_sm"):
        print("Downloading the 'en_core_web_sm' model for spaCy...")
        spacy.cli.download("en_core_web_sm")

    db_connection = connect_to_db()

    if db_connection:
        anime_df = load_data_to_dataframe(db_connection)
        new_df = preprocess_anime_data(anime_df)
        print("Updating the database with preprocessed data...")
        cursor = db_connection.cursor()
        update_data = [(row['content_string'], row['mal_id']) for index, row in new_df.iterrows()]

        update_query = """
        UPDATE anime_data.anime AS a
        SET content_string = data.content_string
        FROM (VALUES %s) AS data(content_string, mal_id)
        WHERE a.mal_id = data.mal_id;
        """

        execute_values(cursor, update_query, update_data)
        db_connection.commit()
        cursor.close()
        close_connection(db_connection)
        print("Database updated successfully.")
    else:
        print("Failed to connect to the database.")

