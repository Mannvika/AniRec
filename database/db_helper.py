import psycopg2
import os

def load_password():
    script_dir = os.path.dirname(os.path.abspath(__file__))    
    password_path = os.path.join(script_dir, 'password')
    with open(password_path, 'r') as file:
        password = file.read().strip()
    return password

def connect_to_db():
    try:
        connection = psycopg2.connect(
            dbname='AniRec',
            user='postgres',
            password=load_password(),
            host='localhost',
            port='5432'
        )
        print("Database connection established successfully.")
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None
    
def close_connection(connection):
    if connection:
        try:
            connection.close()
            print("Database connection closed.")
        except psycopg2.Error as e:
            print(f"Error closing the database connection: {e}")
    else:
        print("No connection to close.")