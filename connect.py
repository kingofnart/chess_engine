import psycopg2, os

def connect():
    try:
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'db'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD')
            )
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error connecting to the database: {error}")
        return -1