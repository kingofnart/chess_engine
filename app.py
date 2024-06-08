from flask import Flask, request, session, jsonify, render_template, url_for, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from game import Game
from connect import connect
import os

app = Flask(__name__)

app.secret_key = os.getenv('CHESS_DB_SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
    
game = Game()

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/move', methods=['POST'])
def move():
    # convert json move info to python object (dict)
    data = request.get_json()
    # data = {'move': ['y1,x1', 'y2,x2']}
    move = data.get('move')
    result = game.make_move(move)
    return jsonify(result)

@app.route('/state', methods=['GET'])
def state():
    result = game.get_state()
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
                cur.execute("SELECT password FROM users WHERE username = %s", (username,))
                user = cur.fetchone()

        if user and check_password_hash(user[0], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
