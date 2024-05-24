from flask import Flask, request, jsonify, url_for, render_template
from game import Game

app = Flask(__name__)
game = Game()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    # convert json move info to python (list)
    data = request.get_json()
    move = data.get('move')
    result = game.make_move(move)
    return jsonify(result)

@app.route('/state', methods=['GET'])
def state():
    result = game.get_state()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
