from connect import connect

def initialize_database():
    conn = connect()
    if conn == -1:
        print("Error connecting to database")
        return
    cur = conn.cursor()

    # Check if the users table exists
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")
    exists = cur.fetchone()[0]

    if not exists:
        # Create tables if they do not exist
        cur.execute('''
        CREATE TABLE users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        );

        CREATE TABLE games (
            game_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id),
            game_history TEXT NOT NULL
        );
                    
        CREATE INDEX idx_games_user_id ON games (user_id);
        ''')

        conn.commit()
        print("Database initialized successfully.")
    else:
        print("Database already initialized.")

    cur.close()
    conn.close()

if __name__ == '__main__':
    initialize_database()