import psycopg2, os

def connect():
    try:
        print("POSTGRES_HOST:", os.getenv('POSTGRES_HOST', 'db'))
        print("POSTGRES_DB:", os.getenv('POSTGRES_DB'))
        print("POSTGRES_USER:", os.getenv('POSTGRES_USER'))
        print("POSTGRES_PASSWORD:", os.getenv('POSTGRES_PASSWORD'))
        conn = psycopg2.connect(host=os.getenv('POSTGRES_HOST', 'db'),
                                database=os.getenv('POSTGRES_DB'),
                                user=os.getenv('POSTGRES_USER'),
                                password=os.getenv('POSTGRES_PASSWORD'))
        print('Connected to the PostgreSQL server.')
        return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error connecting to the database: {error}")
        return -1