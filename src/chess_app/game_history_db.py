from src.chess_app.connect import connect
import json

def store_game(user_id, game_history):
    conn = connect()
    if conn == -1:
        print("Error connecting to database")
        return
    with conn:
        with conn.cursor() as cur:
            game_history_json = json.dumps(game_history)
            cur.execute("INSERT INTO games (user_id, game_history) VALUES (%s, %s) RETURNING game_id;", (user_id, game_history_json))
            game_id = cur.fetchone()[0]
            
            conn.commit()
            cur.close()
            conn.close()

            return game_id

def retrieve_games(user_id):
    conn = connect()
    if conn == -1:
        print("Error connecting to database")
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT game_id, game_history FROM games WHERE user_id = %s;", (user_id,))
            games = cur.fetchall()
            
            user_games = []
            for game in games:
                game_id = game[0]
                game_history = json.loads(game[1])
                user_games.append((game_id, game_history))
            
            cur.close()
            conn.close()

            return user_games