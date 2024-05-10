import sys, numpy as np
sys.path.append('src')
from grid import Grid
from piece import Piece

names = {0: "King", 1: "Queen", 2: "Rook", 3: "Bishop", 4: "Knight", 5: "Pawn"}
# piece type key: 0 = King; 1 = Queen; 2 = Rook; 3 = Knight; 4 = Bishop; 5 = Pawn
# piece id key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
#             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
board = Grid()
grid = board.grid
# NOTE: moves are stored as [[y1,x1],[y2,x2]] b/c grid is grouped by row  
# opening moves
move0 = [[1,0], [2,0]] # a2->a3
move1 = [[1,0], [3,0]] # a2->a4
move2 = [[0,0], [3,0]] # a1->a4
move3 = [[2,0], [3,0]] # a3->a4
move4 = [[6,0], [5,0]] # a7->a6
move5 = [[6,0], [4,0]] # a7->a5
move6 = [[1,0], [4,0]] # a2->a5
move7 = [[6,0], [3,0]] # a7->a4
move8 = [[0,1], [2,2]] # b1->c3
move9 = [[7,1], [5,2]] # b8->c6
move10 = [[0,0], [4,4]] # a1->e5
move11 = [[0,2], [4,4]] # c1->e5
move12 = [[0,3], [4,4]] # d1->e5
move13 = [[0,4], [4,4]] # e1->e5
move14 = [[7,0], [4,4]] # a8->e5
move15 = [[7,2], [4,4]] # c8->e5
move16 = [[7,3], [4,4]] # d8->e5
move17 = [[7,4], [4,4]] # e8->e5
# Fried Liver moves
move18 = [[4,6], [6,5]] # g5->f7
move19 = [[6,3], [4,3]] # d7->d5
move20 = [[7,5], [4,2]] # f8->c5
move21 = [[5,5], [3,4]] # f6->e4
move22 = [[4,6], [3,4]] # g5->e4
move23 = [[0,3], [3,6]] # d1->g4
move24 = [[0,3], [4,3]] # d1->d5

def set_fried_liver(grd):
    grd.grid =  [[grd.w_pcs[2], grd.w_pcs[4], grd.w_pcs[6], grd.w_pcs[1], 
                  grd.w_pcs[0], 0, 0, grd.w_pcs[3]], 
                  [grd.w_pcs[8], grd.w_pcs[9], grd.w_pcs[10], grd.w_pcs[11], 0, 
                   grd.w_pcs[13], grd.w_pcs[14], grd.w_pcs[15]], 
                  [0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, grd.w_pcs[7], 0, grd.w_pcs[12], 0, 0, 0], 
                  [0, 0, 0, 0, grd.b_pcs[12], 0, grd.w_pcs[5], 0], 
                  [0, 0, grd.b_pcs[4], 0, 0, grd.b_pcs[5], 0, 0], 
                  [grd.b_pcs[8], grd.b_pcs[9], grd.b_pcs[10], grd.b_pcs[11], 0, 
                   grd.b_pcs[13], grd.b_pcs[14], grd.b_pcs[15]], 
                  [grd.b_pcs[2], 0, grd.b_pcs[6], grd.b_pcs[1], 
                   grd.b_pcs[0], grd.b_pcs[7], 0, grd.b_pcs[3]]]
    grd.w_coords = np.array([[0,4], [0,3], [0,0], [0,7], [0,1], 
                               [4,6], [0,2], [3,2], [1,0], [1,1], 
                               [1,2], [1,3], [3,4], [1,5], [1,6], [1,7]])
    grd.b_coords = np.array([[7,4], [7,3], [7,0], [7,7], [5,2], 
                               [5,5], [7,3], [7,5], [6,0], [6,1], 
                               [6,2], [6,3], [4,4], [6,5], [6,6], [6,7]])

def test_vaild_move():
    # move0: (valid)
    assert board.valid_move(move0) == 1
    # move1: (valid move)
    assert board.valid_move(move1) == 1
    # move2: (invalid move)
    assert board.valid_move(move2) == 0
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
    # move8: (valid move)
    assert board.valid_move(move8) == 1
    # move9: (valid move)
    assert board.valid_move(move9) == 1
    # move10: (invalid move)
    assert board.valid_move(move10) == 0
    # move11: (invalid move)
    assert board.valid_move(move11) == 0
    # move12: (invalid move)
    assert board.valid_move(move12) == 0
    # move13: (invalid move)
    assert board.valid_move(move13) == 0
    # move14: (invalid move)
    assert board.valid_move(move14) == 0
    # move15: (invalid move)
    assert board.valid_move(move15) == 0
    # move16: (invalid move)
    assert board.valid_move(move16) == 0
    # move17: (invalid move)
    assert board.valid_move(move17) == 0

    # set grid to Fried Liver opening
    set_fried_liver(board)

    # move18: (valid)
    assert board.valid_move(move18) == 1
    # move19: (valid)
    assert board.valid_move(move19) == 1
    # move20: (valid)
    assert board.valid_move(move20) == 1
    # move21: (valid)
    assert board.valid_move(move21) == 1
    # move22: (invalid)
    assert board.valid_move(move22) == 0
    # move23: (valid)
    assert board.valid_move(move23) == 1
    # move24: (invalid)
    assert board.valid_move(move24) == 0

def test_attacked_squares(): 
    # set grid to Fried Liver opening
    set_fried_liver(board)
    board.attacked_squares(0)
    assert np.sum(np.array(board.w_attacked_squares) - np.array([[1, 4], [1, 3], [1, 5], [0, 3], [0, 5], 
                                                                [0, 4], [2, 5], [3, 6], [4, 7], [1, 2], 
                                                                [0, 2], [0, 1], [1, 0], [1, 7], [0, 6], 
                                                                [2, 0], [2, 2], [2, 7], [6, 5], [6, 7], 
                                                                [3, 4], [5, 4], [1, 1], [4, 3], [4, 1], 
                                                                [5, 0], [2, 1], [2, 3], [2, 4], [4, 5], 
                                                                [2, 6]])) == 0
    board.attacked_squares(1)
    assert np.sum(np.array(board.b_attacked_squares) - np.array([[6, 4], [6, 3], [6, 5], [7, 3], [7, 5], 
                                                                 [7, 4], [7, 2], [6, 2], [5, 5], [7, 1], 
                                                                 [6, 0], [7, 6], [6, 7], [3, 1], [3, 3], 
                                                                 [4, 0], [4, 4], [3, 4], [3, 6], [4, 3], 
                                                                 [4, 7], [5, 3], [4, 2], [2, 0], [6, 6], 
                                                                 [5, 1], [5, 0], [5, 2], [5, 4], [3, 5], 
                                                                 [5, 6], [5, 7]])) == 0
    board.reset()
    # set grid with kings on e4 and e5 
    board.grid = [[0 for _ in range(8)], 
                  [0 for _ in range(8)], 
                  [0 for _ in range(8)], 
                  [0, 0, 0, 0, Piece(0,0,0), 0, 0, 0], 
                  [0, 0, 0, 0, Piece(1,0,0), 0, 0, 0], 
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
    assert np.sum(np.array(board.w_attacked_squares) - np.array([])) == 0
    board.attacked_squares(0)
    assert np.sum(np.array(board.w_attacked_squares) - [np.array([3, 3]), np.array([3, 2]), 
                                                        np.array([3, 4]), np.array([5, 3]), 
                                                        np.array([5, 2]), np.array([5, 4]), 
                                                        np.array([4, 2]), np.array([4, 4])]) == 0
    assert np.sum(np.array(board.b_attacked_squares) - np.array([])) == 0
    board.attacked_squares(1)
    assert np.sum(np.array(board.b_attacked_squares) - [np.array([3, 4]), np.array([3, 3]), 
                                                        np.array([3, 5]), np.array([5, 4]), 
                                                        np.array([5, 3]), np.array([5, 5]), 
                                                        np.array([4, 3]), np.array([4, 5])]) == 0
