from flask import Flask, request, jsonify, url_for, render_template
from game import Game

app = Flask(__name__)
game = Game()

@app.route('/')
def index():
    return render_template('index.html')

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

if __name__ == '__main__':
    app.run(debug=True)
