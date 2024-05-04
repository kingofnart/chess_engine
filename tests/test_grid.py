import sys
sys.path.append('src')
from grid import Grid

names = {0: "King", 1: "Queen", 2: "Rook", 3: "Bishop", 4: "Knight", 5: "Pawn"}
board = Grid()
grid = board.grid
move0 = [[1,0], [2,0]] # a2->a3
move1 = [[1,0], [3,0]] # a2->a4
move2 = [[0,0], [3,0]] # a1->a4
move3 = [[2,0], [3,0]] # a3->a4
move4 = [[6,0], [5,0]] # a7->a6
move5 = [[6,0], [4,0]] # a7->a5

def test_vaild_move():
    # move0: (valid)
    assert board.valid_move(move0) == 1
    # move1: (invalid move)
    assert board.valid_move(move1) == 0
    # move2: (invalid piecce id)
    assert board.valid_move(move2) == -1
    # move3: (invalid piece)
    assert board.valid_move(move3) == -1
    # move4: (valid)
    assert board.valid_move(move4) == 1
    # move5: (invalid move)
    assert board.valid_move(move5) == 0