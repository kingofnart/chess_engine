import numpy as np
from piece import Piece

class Grid():
    def __init__(self):
        # color key: 0 = white, 1 = black
        self.w_pcs = [Piece(0,0), Piece(0,1), Piece(0,2), Piece(0,2), Piece(0,3), Piece(0,3), Piece(0,4), Piece(0,4), Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5)]
        self.b_pcs = [Piece(1,0), Piece(1,1), Piece(1,2), Piece(1,2), Piece(1,3), Piece(1,3), Piece(1,4), Piece(1,4), Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5)]
        # coord key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
        self.w_coords = np.array([[4,0], [3,0], [0,0], [7,0], [1,0], [6,0], [3,0], [5,0], [0,1], [1,1], [2,1], [3,1], [4,1], [5,1], [6,1], [7,1]])
        self.b_coords = np.array([[4,7], [3,7], [0,7], [7,7], [1,7], [6,7], [3,7], [5,7], [0,6], [1,6], [2,6], [3,6], [4,6], [5,6], [6,6], [7,6]])
        self.w_attacked_squares = np.array([[0,3], [1,3], [2,3], [3,3], [4,3], [5,3], [6,3], [7,3]])
        self.b_attacked_squares = np.array([[0,5], [1,5], [2,5], [3,5], [4,5], [5,5], [6,5], [7,5]])
        self.grid = [[self.w_pcs[2], self.w_pcs[4], self.w_pcs[6], self.w_pcs[1], self.w_pcs[0], self.w_pcs[7], self.w_pcs[5], self.w_pcs[3]], 
                     self.w_pcs[8:], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     self.b_pcs[8:], 
                     [self.b_pcs[2], self.b_pcs[4], self.b_pcs[6], self.b_pcs[1], self.b_pcs[0], self.b_pcs[7], self.b_pcs[5], self.b_pcs[3]]]

    def attacked_squares(self, color):
        if color:
            pieces = self.b_pcs
            coords = self.b_coords
            attacked_squares = self.b_attacked_squares
        else:
            pieces = self.w_pcs
            coords = self.w_coords
            attacked_squares = self.w_attacked_squares
        for piece, coord in zip(pieces, coords):
            match piece.id:
                # king
                case 0:
                    if coord[0] != 0:
                        attacked_squares.append([coord + [-1,0]])
                        if coord[1] != 0:
                            attacked_squares.append(coord + [-1,-1])
                        if coord[1] != 7:
                            attacked_squares.append(coord + [-1,1])
                    if coord[0] != 7:
                        attacked_squares.append([coord + [1,0]])
                        if coord[1] != 0:
                            attacked_squares.append(coord + [1,-1])
                        if coord[1] != 7:
                            attacked_squares.append(coord + [1,1])
                    if coord[1] != 0:
                        attacked_squares.append(coord + [0,-1])
                    if coord[1] != 7:
                        attacked_squares.append(coord + [0,1])
                # queen
                #case 1:
                
                # rook
                #case 2:

                # bishop
                #case 3:

                # knight
                #case 4:

                # pawn
                #case 5:

                case _:
                    return -1

    # 0 = King, 1 = Queen, 2 = Rook, 3 = Bishop, 4 = Knight, 5 = Pawn
    def valid_move(self, move):
        piece = self.grid[move[0][0]][move[0][1]]
        
        if (piece != 0):
            match piece.id:
                # king
                #case 0:  

                # queen
                #case 1:

                # rook
                #case 2:

                # bishop
                #case 3:

                # knight
                #case 4:

                # pawn
                case 5:
                    if piece.color == 0:
                        if move[0][0] == move[1][0] - 1:
                            return 1
                        else: return 0
                    elif piece.color == 1:
                        if move[0][0] == move[1][0] + 1:
                            return 1
                        else: return 0
                case _:
                    return -2
        else:
            return -1