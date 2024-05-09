import numpy as np
from piece import Piece

class Grid():
    def __init__(self):
        # color key: 0 = white, 1 = black
        self.w_pcs = [Piece(0,0), Piece(0,1), Piece(0,2), Piece(0,2), 
                      Piece(0,3), Piece(0,3), Piece(0,4), Piece(0,4), 
                      Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5), 
                      Piece(0,5), Piece(0,5), Piece(0,5), Piece(0,5)]
        self.b_pcs = [Piece(1,0), Piece(1,1), Piece(1,2), Piece(1,2), 
                      Piece(1,3), Piece(1,3), Piece(1,4), Piece(1,4), 
                      Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5), 
                      Piece(1,5), Piece(1,5), Piece(1,5), Piece(1,5)]
        # coord key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
        #             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
        self.w_coords = np.array([[4,0], [3,0], [0,0], [7,0], [1,0], 
                                  [6,0], [3,0], [5,0], [0,1], [1,1], 
                                  [2,1], [3,1], [4,1], [5,1], [6,1], [7,1]])
        self.b_coords = np.array([[4,7], [3,7], [0,7], [7,7], [1,7], 
                                  [6,7], [3,7], [5,7], [0,6], [1,6], 
                                  [2,6], [3,6], [4,6], [5,6], [6,6], [7,6]])
        self.w_attacked_squares = np.array([[0,2], [1,2], [2,2], [3,2], 
                                            [4,2], [5,2], [6,2], [7,2]])
        self.b_attacked_squares = np.array([[0,5], [1,5], [2,5], [3,5], 
                                            [4,5], [5,5], [6,5], [7,5]])
        self.grid = [[self.w_pcs[2], self.w_pcs[4], self.w_pcs[6], self.w_pcs[1], 
                      self.w_pcs[0], self.w_pcs[7], self.w_pcs[5], self.w_pcs[3]], 
                     self.w_pcs[8:], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     [0 for _ in range(8)], 
                     self.b_pcs[8:], 
                     [self.b_pcs[2], self.b_pcs[4], self.b_pcs[6], self.b_pcs[1], 
                      self.b_pcs[0], self.b_pcs[7], self.b_pcs[5], self.b_pcs[3]]]

    def attacked_squares(self, color):
        attacked_list = []
        # get correct pieces/coordinates
        if color:
            pieces = self.b_pcs
            coords = self.b_coords
        else:
            pieces = self.w_pcs
            coords = self.w_coords
        for piece, coord in zip(pieces, coords):
            if not piece.captured:
                match piece.id:
                    # king
                    case 0:
                        # only move one square, no moving off the board
                        if coord[0] != 0:
                            attacked_list.append(coord + [-1,0])
                            if coord[1] != 0:
                                attacked_list.append(coord + [-1,-1])
                            if coord[1] != 7:
                                attacked_list.append(coord + [-1,1])
                        if coord[0] != 7:
                            attacked_list.append(coord + [1,0])
                            if coord[1] != 0:
                                attacked_list.append(coord + [1,-1])
                            if coord[1] != 7:
                                attacked_list.append(coord + [1,1])
                        if coord[1] != 0:
                            attacked_list.append(coord + [0,-1])
                        if coord[1] != 7:
                            attacked_list.append(coord + [0,1])
                    # queen
                    case 1:
                        # just gonna search all 8 directions in order
                        attacked_list.append(self.line_search(1, 0, coord)) # 0
                        attacked_list.append(self.line_search(1, 1, coord)) # pi/4
                        attacked_list.append(self.line_search(0, 1, coord)) # pi/2
                        attacked_list.append(self.line_search(-1, 1, coord)) # 3pi/4
                        attacked_list.append(self.line_search(-1, 0, coord)) # pi
                        attacked_list.append(self.line_search(-1, -1, coord)) # 5pi/4
                        attacked_list.append(self.line_search(0, -1, coord)) # 3pi/2
                        attacked_list.append(self.line_search(1, -1, coord)) # 7pi/4

                    # rook
                    case 2:
                        # only horizontals & verticals
                        attacked_list.append(self.line_search(1, 0, coord)) # 0
                        attacked_list.append(self.line_search(0, 1, coord)) # pi/2
                        attacked_list.append(self.line_search(-1, 0, coord)) # pi
                        attacked_list.append(self.line_search(0, -1, coord)) # 3pi/2

                    # knight
                    case 3:
                        # check for move 2 squares in one cardinal directrion
                        # then check for move 1 square perpendicular
                        if coord[0] >= 2: # move up
                            if coord[1] > 0:
                                attacked_list.append([coord[0] - 2, coord[1] - 1])
                            if coord[1] < 7:
                                attacked_list.append([coord[0] - 2, coord[1] + 1])
                        if coord[0] <= 5: # move down
                            if coord[1] > 0:
                                attacked_list.append([coord[0] + 2, coord[1] - 1])
                            if coord[1] < 7:
                                attacked_list.append([coord[0] + 2, coord[1] + 1])
                        if coord[1] >= 2: # move left
                            if coord[0] > 0:
                                attacked_list.append([coord[0] - 1, coord[1] - 2])
                            if coord[0] < 7:
                                attacked_list.append([coord[0] + 1, coord[1] - 2])
                        if coord[1] <= 5: # move right
                            if coord[0] > 0:
                                attacked_list.append([coord[0] - 1, coord[1] + 2])
                            if coord[0] < 7:
                                attacked_list.append([coord[0] + 1, coord[1] + 2])
                    
                    # bishop
                    case 4:
                        # only diagonals
                        attacked_list.append(self.line_search(1, 1, coord)) # pi/4
                        attacked_list.append(self.line_search(-1, 1, coord)) # 3pi/4
                        attacked_list.append(self.line_search(-1, -1, coord)) # 5pi/4
                        attacked_list.append(self.line_search(1, -1, coord)) # 7pi/4

                    # pawn
                    case 5:
                        if color: # black
                            if coord[1] > 0:
                                attacked_list.append([coord[0] - 1, coord[1] - 1])
                            if coord[1] < 7:
                                attacked_list.append([coord[0] - 1, coord[1] + 1])
                        else:
                            if coord[1] > 0:
                                attacked_list.append([coord[0] + 1, coord[1] - 1])
                            if coord[1] < 7:
                                attacked_list.append([coord[0] + 1, coord[1] + 1])
                    
                    case _:
                        raise Exception("Invalid piece id")
        # update correct list
        if color:
            self.b_attacked_squares = attacked_list
        else: self.w_attacked_squares = attacked_list

    # helper function for attacked_squares to search along vert/hor/diag lines
    # for queen, rook, bishop
    def line_search(self, y, x, coord): # x, y = -1,0,1 to set search direction
        search = True
        lst = []
        # don't set square piece is on to attacked, piece cant attack itself!
        idx = [coord[0] + y, coord[1] + x] 
        # want to search in straight line until you find piece or edge of board
        while idx[0] <= 7 and idx[0] >= 0 and idx[1] <= 7 and idx[1] >= 0 and search:
            lst.append(idx.copy())
            if self.grid[idx[0]][idx[1]] != 0: # found piece, stop search
                search = False
            idx[0] = idx[0] + y
            idx[1] = idx[1] + x
        return lst
    
    def valid_move(self, move):
        # move = [[x1, y1], [x2, y2]]
        piece = self.grid[move[0][0]][move[0][1]]
        if piece:
            # first make sure you're not capturing your own piece
            piece2 = self.grid[move[1][0]][move[1][1]]
            if piece2:
                if piece2.color == piece.color:
                    return 0
            match piece.id:
                
                # king
                case 0:
                    if np.sqrt((move[0][0]-move[1][0])**2 + (move[1][0]-move[1][1])**2) <= np.sqrt(2):
                        if move[1][0] >= 0 and move[1][0] <= 7 and move[1][1] >= 0 and move[1][1] <= 7:
                            return 1
                    return 0

                # queen
                case 1:
                    if move[1] in (self.line_search(1, 0, move[0])):
                        return 1
                    elif move[1] in (self.line_search(1, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(0, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, 0, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, -1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(0, -1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(1, -1, move[0])):
                        return 1
                    else: return 0

                # rook
                case 2:
                    if move[1] in (self.line_search(1, 0, move[0])):
                        return 1
                    elif move[1] in (self.line_search(0, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, 0, move[0])):
                        return 1
                    elif move[1] in (self.line_search(0, -1, move[0])):
                        return 1
                    else: return 0

                # knight
                case 3:
                    if move[0][0] + 2 == move[1][0] or move[0][0] - 2 == move[1][0]:
                        if move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]:
                            return 1
                    elif move[0][1] + 2 == move[1][1] or move[0][1] - 2 == move[1][1]:
                        if move[0][0] + 1 == move[1][0] or move[0][0] - 1 == move[1][0]:
                            return 1
                    else: return 0

                
                # bishop
                case 4:
                    if move[1] in (self.line_search(1, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, 1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(-1, -1, move[0])):
                        return 1
                    elif move[1] in (self.line_search(1, -1, move[0])):
                        return 1
                    else: return 0

                # pawn
                case 5:
                    if piece.color == 0: # white
                        sign = 1 
                    else: # black
                        sign = -1 
                    if move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]: # capture
                        if move[0][0] + sign != move[1][0]: # invalid move
                            return 0
                        elif self.grid[move[1][0]][move[1][1]] == 0: # no piece forward-diagonal from pawn
                            if self.grid[move[1][0] + 1][move[1][1]] != 0: # en pesant?
                                pawn2 = self.grid[move[1][0] + 1][move[1][1]]
                                if pawn2.enpassant:
                                    pawn2.set_captured(1)
                                    return 1
                            elif self.grid[move[1][0] - 1][move[1][1]] != 0:
                                pawn2 = self.grid[move[1][0] - 1][move[1][1]]
                                if pawn2.enpassant:
                                    pawn2.set_captured(1)
                                    return 1
                            else: return 0
                        else: # valid move
                            return 1
                    if move[0][0] + sign == move[1][0]: # valid move
                        return 1    
                    elif move[0][0] + 2*sign == move[1][0] and piece.moved == 0: # valid move
                        piece.enpassant = 1
                        return 1
                    else: # invalid move
                        return 0
                case _: # invalid piece id
                    return -2
        else: # not piece
            return -1