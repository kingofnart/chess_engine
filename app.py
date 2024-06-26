from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from game import Game
from connect import connect
import os
import sys
import logging

gameControllers = {}
printing = False
gameControllers[0] = Game(0, printing)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('CHESS_DB_SECRET_KEY')
#DATABASE_URL = os.getenv('DATABASE_URL')

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

    @staticmethod
    def get(user_id):
        conn = connect()
        if conn == -1:
            return None
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username, password FROM users WHERE user_id = %s", (user_id,))
                user_data = cur.fetchone()
                if not user_data:
                    return None
                return User(user_id=user_data[0], username=user_data[1], password=user_data[2])


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@app.route('/')
@login_required
def index():
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username)
    else:
        return render_template('login.html')


@app.route('/move', methods=['POST'])
@login_required
def move():
    # convert json move info to python object (dict)
    data = request.get_json()
    # data = {'move': ['y1,x1', 'y2,x2']}
    move = data.get('move')
    gameID = int(data.get('gameID'))
    if gameID is not None and gameID in gameControllers:
        game = gameControllers[gameID]
        result = game.make_move(move)
    else:
        print(f"Game {gameID} not found")
        result = {"error": "Invalid game ID"}
    return jsonify(result)


@app.route('/state', methods=['GET'])
@login_required
def state():
    result = gameControllers[0].get_state() # only used for game actively being played
    return jsonify(result)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        conn = connect()
        if conn == -1:
            return "Error connecting to database", 500
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT username FROM users WHERE username = %s", (username,))
                existing_user = cur.fetchone()
                if existing_user:
                    return render_template('register.html', error="Username already taken")
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
                conn.commit()

        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = connect()
        if conn == -1:
            return "Error connecting to database", 500
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT user_id, username, password FROM users WHERE username = %s", (username,))
                user_data = cur.fetchone()

        if user_data and check_password_hash(user_data[2], password):
            user = User(user_data[0], user_data[1], user_data[2])
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/game_history')
@login_required
def game_history():
    user_id = current_user.id
    games = get_user_games(user_id) 
    for game in games:
        gameC = Game(game["id"])
        gameControllers[game["id"]] = gameC
    return render_template('game_history.html', username=current_user.username, games=games)


# helper for game_history()
def get_user_games(user_id):
    conn = connect()
    if conn == -1:
        return []
    with conn:
        with conn.cursor() as cur:
            cur.execute("SELECT game_id, game_history, game_time, opponent, color FROM games WHERE user_id = %s", (user_id,))
            games = cur.fetchall()
    return [{"id": game[0], "moves": game[1], "time": game[2], "opponent": game[3], "color": game[4]} for game in games]


if __name__ == '__main__':
    app.run(debug=True)