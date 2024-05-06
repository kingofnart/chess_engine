import sys, numpy as np
sys.path.append('src')
from grid import Grid
from piece import Piece

names = {0: "King", 1: "Queen", 2: "Rook", 3: "Bishop", 4: "Knight", 5: "Pawn"}
board = Grid()
grid = board.grid
move0 = [[1,0], [2,0]] # a2->a3
move1 = [[1,0], [3,0]] # a2->a4
move2 = [[0,0], [3,0]] # a1->a4
move3 = [[2,0], [3,0]] # a3->a4
move4 = [[6,0], [5,0]] # a7->a6
move5 = [[6,0], [4,0]] # a7->a5
move6 = [[1,0], [4,0]] # a2->a5
move7 = [[6,0], [3,0]] # a7->a4

def test_vaild_move():
    # move0: (valid)
    assert board.valid_move(move0) == 1
    # move1: (valid move)
    assert board.valid_move(move1) == 1
    # move2: (invalid piecce id)
    assert board.valid_move(move2) == -2
    # move3: (invalid piece)
    assert board.valid_move(move3) == -1
    # move4: (valid)
    assert board.valid_move(move4) == 1
    # move5: (valid move)
    assert board.valid_move(move5) == 1
    # move6: (invalid move)
    assert board.valid_move(move6) == 0
    # move7: (invalid move)
    assert board.valid_move(move7) == 0

def test_attacked_squares():
    # set grid with kings on e4 and e5
    board.grid = [[0 for _ in range(8)], 
                  [0 for _ in range(8)], 
                  [0 for _ in range(8)], 
                  [0, 0, 0, 0, Piece(0,0), 0, 0, 0], 
                  [0, 0, 0, 0, Piece(1,0), 0, 0, 0], 
                  [0 for _ in range(8)], 
                  [0 for _ in range(8)], 
                  [0 for _ in range(8)]]
    # set all other pieces to captured
    for i in range(1, 16):
        board.w_pcs[i].captured = 1
        board.b_pcs[i].captured = 1
    # update king coordinates
    board.w_coords[0] = [4,3]
    board.b_coords[0] = [4,4]
    assert np.sum(np.array(board.w_attacked_squares) - np.array([[0,2], [1,2], [2,2], [3,2], [4,2], [5,2], [6,2], [7,2]])) == 0
    board.attacked_squares(0)
    assert np.sum(np.array(board.w_attacked_squares) - [np.array([3, 3]), np.array([3, 2]), 
                                                        np.array([3, 4]), np.array([5, 3]), 
                                                        np.array([5, 2]), np.array([5, 4]), 
                                                        np.array([4, 2]), np.array([4, 4])]) == 0
    assert np.sum(np.array(board.b_attacked_squares) - np.array([[0,5], [1,5], [2,5], [3,5], [4,5], [5,5], [6,5], [7,5]])) == 0
    board.attacked_squares(1)
    assert np.sum(np.array(board.b_attacked_squares) - [np.array([3, 4]), np.array([3, 3]), 
                                                        np.array([3, 5]), np.array([5, 4]), 
                                                        np.array([5, 3]), np.array([5, 5]), 
                                                        np.array([4, 3]), np.array([4, 5])]) == 0
