import sys
import os

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import pandas as pd
import spacy
import psycopg2
from database.db_helper import connect_to_db, close_connection

# Function to load database content into a pandas DataFrame
def load_data_to_dataframe(connection):
    query = "SELECT * FROM anime_data.anime;"
    df = pd.read_sql_query(query, connection)
    return df

if __name__ == "__main__":
    db_connection = connect_to_db()
    if db_connection:
        anime_df = load_data_to_dataframe(db_connection)
        print("Data loaded into DataFrame successfully.")
        print(anime_df.head())
        close_connection(db_connection)
    else:
        print("Failed to connect to the database.")

