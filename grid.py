import numpy as np
import copy
from piece import Piece

class Grid():
    

    def __init__(self):
        
        # color key: 0 = white, 1 = black
        self.color_names = {0: "White", 1: "Black"}
        self.w_pcs = [Piece(0,0,0), Piece(0,1,1), Piece(0,2,2), Piece(0,2,3), 
                      Piece(0,3,4), Piece(0,3,5), Piece(0,4,6), Piece(0,4,7), 
                      Piece(0,5,8), Piece(0,5,9), Piece(0,5,10), Piece(0,5,11), 
                      Piece(0,5,12), Piece(0,5,13), Piece(0,5,14), Piece(0,5,15)]
        self.b_pcs = [Piece(1,0,0), Piece(1,1,1), Piece(1,2,2), Piece(1,2,3), 
                      Piece(1,3,4), Piece(1,3,5), Piece(1,4,6), Piece(1,4,7), 
                      Piece(1,5,8), Piece(1,5,9), Piece(1,5,10), Piece(1,5,11), 
                      Piece(1,5,12), Piece(1,5,13), Piece(1,5,14), Piece(1,5,15)]
        # piece id key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
        #             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
        self.w_coords = np.array([[0,4], [0,3], [0,0], [0,7], [0,1], 
                                  [0,6], [0,2], [0,5], [1,0], [1,1], 
                                  [1,2], [1,3], [1,4], [1,5], [1,6], [1,7]])
        self.b_coords = np.array([[7,4], [7,3], [7,0], [7,7], [7,1], 
                                  [7,6], [7,2], [7,5], [6,0], [6,1], 
                                  [6,2], [6,3], [6,4], [6,5], [6,6], [6,7]])
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
        # list for caluculating material difference
        self.material_w = np.array([0,9,5,5,3,3,3,3,1,1,1,1,1,1,1,1])
        self.material_b = np.array([0,9,5,5,3,3,3,3,1,1,1,1,1,1,1,1])
        self.material_diff = 0
        # initialize lists
        self.board_history = []
        self.move_history = []
        self.attacked_squares_w = []
        self.attacked_squares_b = []
        self.valid_moves_w = []
        self.valid_moves_b = []
        # want to save initial board state to history as well
        self.update_history()
        # special move flags
        self.someone_attempting_enpassant_move = False
        self.castle_queenside = 0
        self.castle_kingside = 0
        self.queening = None  # NOTE self.queening = None for not queening, piece object (the pawn) otherwise
        # popluate attacked_squares and valid_moves for white and black
        self.attacked_squares(0, validation=1)
        self.attacked_squares(1, validation=1)
        # reset any en passant flags set by attacked_squares call
        self.unenpassant(0)
        self.unenpassant(1)


    # getters
    def get_someone_attempting_enpassant_move(self):
        return self.someone_attempting_enpassant_move
    def get_castle_kingside(self):
        return self.castle_kingside
    def get_castle_queenside(self):
        return self.castle_queenside
    def get_queening(self):
        return self.queening
    def get_material_diff(self):
        return self.material_diff
    def get_valid_moves(self, color):
        if color:
            return self.valid_moves_b
        else:
            return self.valid_moves_w
    

    # setters
    def set_someone_attempting_enpassant_move(self, input):
       self.someone_attempting_enpassant_move = input
    def set_castle_kingside(self, input):
        self.castle_kingside = input
    def set_castle_queenside(self, input):
        self.castle_queenside = input
    def set_queening(self, input):
        self.queening = input
    def set_white_coords(self, new_coords):
        self.w_coords = np.array(new_coords)
    def set_black_coords(self, new_coords):
        self.b_coords = np.array(new_coords)


    # function to reset board to starting position  
    def reset(self):
        for piece in self.w_pcs:
            piece.set_captured(0)
            piece.set_enpassant(0)
            piece.set_moved(0)
        for piece in self.b_pcs:
            piece.set_captured(0)
            piece.set_enpassant(0)
            piece.set_moved(0)
        self.w_pcs = [Piece(0,0,0), Piece(0,1,1), Piece(0,2,2), Piece(0,2,3), 
                      Piece(0,3,4), Piece(0,3,5), Piece(0,4,6), Piece(0,4,7), 
                      Piece(0,5,8), Piece(0,5,9), Piece(0,5,10), Piece(0,5,11), 
                      Piece(0,5,12), Piece(0,5,13), Piece(0,5,14), Piece(0,5,15)]
        self.b_pcs = [Piece(1,0,0), Piece(1,1,1), Piece(1,2,2), Piece(1,2,3), 
                      Piece(1,3,4), Piece(1,3,5), Piece(1,4,6), Piece(1,4,7), 
                      Piece(1,5,8), Piece(1,5,9), Piece(1,5,10), Piece(1,5,11), 
                      Piece(1,5,12), Piece(1,5,13), Piece(1,5,14), Piece(1,5,15)]
        self.w_coords = np.array([[0,4], [0,3], [0,0], [0,7], [0,1], 
                                  [0,6], [0,2], [0,5], [1,0], [1,1], 
                                  [1,2], [1,3], [1,4], [1,5], [1,6], [1,7]])
        self.b_coords = np.array([[7,4], [7,3], [7,0], [7,7], [7,1], 
                                  [7,6], [7,2], [7,5], [6,0], [6,1], 
                                  [6,2], [6,3], [6,4], [6,5], [6,6], [6,7]])
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
        # reset lists
        self.material_w = [0,9,5,5,3,3,3,3,1,1,1,1,1,1,1,1]
        self.material_b = [0,9,5,5,3,3,3,3,1,1,1,1,1,1,1,1]
        self.board_history = []
        self.move_history = []
        self.attacked_squares_w = []
        self.attacked_squares_b = []
        self.valid_moves_w = []
        self.valid_moves_b = []
        self.update_history()
        # reset special move flags
        self.someone_attempting_enpassant_move = False
        self.castle_queenside = 0
        self.castle_kingside = 0
        self.queening = None  
        self.attacked_squares(0, validation=1)
        self.attacked_squares(1, validation=1)
        self.unenpassant(0)
        self.unenpassant(1)
    

    # function to save list of all squares attacked by a color
    # validation flag is if you want to store all valid moves
    # don't want to validate if im checking attacked squares on tmp grid for king safety
    def attacked_squares(self, color, validation=0):
        
        attacked_list = []
        # get references to correct lists
        if color:
            self.attacked_squares_b = []
            # updating attacked_list will also update self.attacked_squares_b
            attacked_list = self.attacked_squares_b
            pieces = self.b_pcs
            coords = self.b_coords
        else:
            self.attacked_squares_w = []
            # updating attacked_list will also update self.attacked_squares_w
            attacked_list = self.attacked_squares_w
            pieces = self.w_pcs
            coords = self.w_coords
        if validation:
            if color:  # black
                self.valid_moves_b = []
                valid_moves = self.valid_moves_b
            else:  # white
                self.valid_moves_w = []
                valid_moves = self.valid_moves_w
        else:
            valid_moves = None
        for piece, coord in zip(pieces, coords):
            if not piece.captured:
                match piece.type:
                    
                    # king
                    case 0:
                        # only move one square, no moving off the board
                        if coord[0] != 0:
                            c2 = (coord + [-1,0]).tolist()
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] != 0:
                                c2 = (coord + [-1,-1]).tolist()
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] != 7:
                                c2 = (coord + [-1,1]).tolist()
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[0] != 7:
                            c2 = (coord + [1,0]).tolist()
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                               self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] != 0:
                                c2 = (coord + [1,-1]).tolist()
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] != 7:
                                c2 = (coord + [1,1]).tolist()
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[1] != 0:
                            c2 = (coord + [0,-1]).tolist()
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[1] != 7:
                            c2 = (coord + [0,1]).tolist()
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                    
                    # queen
                    case 1:
                        # just gonna search all 8 directions in order
                        lst = self.line_search(0, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # 0
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 0, coord, get_valid=validation, valid_mvs=valid_moves)  # pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # 3pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(0, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # pi
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # 5pi/4
                        self.add_to_list(attacked_list, lst) 
                        lst = self.line_search(-1, 0, coord, get_valid=validation, valid_mvs=valid_moves)  # 3pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # 7pi/4
                        self.add_to_list(attacked_list, lst)

                    # rook
                    case 2:
                        # only horizontals & verticals
                        lst = self.line_search(0, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # 0
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 0, coord, get_valid=validation, valid_mvs=valid_moves)  # pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(0, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # pi
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 0, coord, get_valid=validation, valid_mvs=valid_moves)  # 3pi/2
                        self.add_to_list(attacked_list, lst)

                    # knight
                    case 3:
                        # check for move 2 squares in one cardinal directrion
                        # then check for move 1 square perpendicular
                        if coord[0] >= 2:  # move up
                            if coord[1] > 0:
                                c2 = [coord[0] - 2, coord[1] - 1]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] < 7:
                                c2 = [coord[0] - 2, coord[1] + 1]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[0] <= 5:  # move down
                            if coord[1] > 0:
                                c2 = [coord[0] + 2, coord[1] - 1]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[1] < 7:
                                c2 = [coord[0] + 2, coord[1] + 1]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[1] >= 2:  # move left
                            if coord[0] > 0:
                                c2 = [coord[0] - 1, coord[1] - 2]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[0] < 7:
                                c2 = [coord[0] + 1, coord[1] - 2]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[1] <= 5:  # move right
                            if coord[0] > 0:
                                c2 = [coord[0] - 1, coord[1] + 2]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if coord[0] < 7:
                                c2 = [coord[0] + 1, coord[1] + 2]
                                self.add_to_list(attacked_list, [c2])
                                if validation:
                                    self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                    
                    # bishop
                    case 4:
                        # only diagonals
                        lst = self.line_search(1, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # 3pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, -1, coord, get_valid=validation, valid_mvs=valid_moves)  # 5pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 1, coord, get_valid=validation, valid_mvs=valid_moves)  # 7pi/4
                        self.add_to_list(attacked_list, lst)

                    # pawn
                    case 5:
                        if color:  # black
                            sign = -1
                        else:  # white
                            sign = 1
                        if coord[1] > 0:
                            c2 = [coord[0] + sign, coord[1] - 1]
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        if coord[1] < 7:
                            c2 = [coord[0] + sign, coord[1] + 1]
                            self.add_to_list(attacked_list, [c2])
                            if validation:
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                        # also have to check non-captures for valid moves
                        if validation:
                            c2 = [coord[0] + sign, coord[1]]
                            self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                            if not piece.get_moved():
                                c2 = [coord[0] + 2*sign, coord[1]]
                                self.update_validmoves_lst([coord.tolist(), c2], color, valid_moves)
                    
                    case _:
                        raise Exception("Invalid piece id")
                               

    # helper function for attacked_squares to add each element of list only if it's unique
    # might want to change attacked_squares to set of tuples instead of list of lists
    def add_to_list(self, old, new):
        
        if len(new) > 0:
            for x in new:
                if x not in old:
                    old.append(x) 


    # helper function for attacked_squares to search along vert/hor/diag lines
    # for queen, rook, bishop
    def line_search(self, y, x, coord, get_valid = False, valid_mvs=None): # x, y \in {-1,0,1} to set search direction
        search = True
        lst = []
        color = self.grid[coord[0]][coord[1]].get_color()
        # don't set square piece is on to attacked, piece cant attack itself!
        idx = [coord[0] + y, coord[1] + x] 
        # want to search in straight line until you find piece or edge of board
        while idx[0] <= 7 and idx[0] >= 0 and idx[1] <= 7 and idx[1] >= 0 and search:
            lst.append(idx.copy())
            if get_valid:
                if color:
                    self.update_validmoves_lst([coord.tolist(), idx], color, valid_mvs)
                else:
                    self.update_validmoves_lst([coord.tolist(), idx], color, valid_mvs)
            if self.grid[idx[0]][idx[1]] != 0:  # found piece, stop search
                search = False
            idx[0] = idx[0] + y
            idx[1] = idx[1] + x
        return lst
    

    # function to test if move is valid
    def valid_move(self, move, color, set_enpassant=0):
        # move = [[y1, x1], [y2, x2]]
        piece = self.grid[move[0][0]][move[0][1]]
        if piece:
            # check to make sure you're moving the right color piece
            if piece.color == color:
                # make sure you're not capturing your own piece
                piece2 = self.grid[move[1][0]][move[1][1]]
                if piece2:
                    if piece2.color == color:
                        return 0
                
                match piece.type:
                    
                    # king
                    case 0:
                        dif1 = np.abs(move[0][0] - move[1][0])
                        dif2 = np.abs(move[0][1] - move[1][1])
                        # normal king move
                        if dif1 <= 1 and dif2 <= 1:
                            if move[1][0] >= 0 and move[1][0] <= 7 and move[1][1] >= 0 and move[1][1] <= 7:
                                return 1
                        # castling
                        # requirements: king and rook can't have moved yet
                        # no pieces in between king and rook
                        # king doesn't move through check
                        # king moves two squares left or right
                        # rook placed next to king on the other side than it used to be
                        elif move[0][1] + 2 == move[1][1]:  # caslting kingside
                            # make sure squares between king and rook are empty
                            if self.grid[move[0][0]][move[0][1] + 1] != 0 or self.grid[move[0][0]][move[0][1] + 2] != 0:
                                return 0
                            if color:
                                atck_lst = self.attacked_squares_w
                                # check black h rook and king haven't moved yet
                                if self.b_pcs[3].get_moved() or piece.get_moved():
                                    return 0
                            else:
                                atck_lst = self.attacked_squares_b
                                # check white h rook and king haven't moved yet
                                if self.w_pcs[3].get_moved() or piece.get_moved():
                                    return 0
                            # cant castle through, out of, or into check
                            for pos in atck_lst:
                                if move[0][0] == pos[0] and move[0][1] == pos[1]:
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] + 1 == pos[1]:
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] + 2 == pos[1]:
                                    return 0
                            self.set_castle_kingside(1)
                            return 1
                        elif move[0][1] - 2 == move[1][1]:  # caslting queenside
                            # make sure squares between king and rook are empty
                            if self.grid[move[0][0]][move[0][1] - 1] != 0 or self.grid[move[0][0]][move[0][1] - 2] != 0 \
                                or self.grid[move[0][0]][move[0][1] - 3] != 0:
                                return 0
                            if color:
                                atck_lst = self.attacked_squares_w
                                # check black a rook and king haven't moved yet
                                if self.b_pcs[2].get_moved() or piece.get_moved():
                                    return 0
                            else:
                                atck_lst = self.attacked_squares_b
                                # check white a rook and king haven't moved yet
                                if self.w_pcs[2].get_moved() or piece.get_moved():
                                    return 0
                            # cant castle through, out of, or into check
                            for pos in atck_lst:
                                if move[0][0] == pos[0] and move[0][1] == pos[1]:
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] - 1 == pos[1]:
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] - 2 == pos[1]:
                                    return 0
                            self.set_castle_queenside(1)
                            return 1
                        return 0

                    # queen
                    case 1: 
                        for pos in self.line_search(1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(0, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(0, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        else: 
                            return 0

                    # rook
                    case 2:
                        for pos in self.line_search(1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(0, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(0, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        else: 
                            return 0

                    # knight
                    case 3:
                        if move[0][0] + 2 == move[1][0] or move[0][0] - 2 == move[1][0]:
                            if move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]:
                                return 1
                        elif move[0][1] + 2 == move[1][1] or move[0][1] - 2 == move[1][1]:
                            if move[0][0] + 1 == move[1][0] or move[0][0] - 1 == move[1][0]:
                                return 1
                        else: 
                            return 0

                    # bishop
                    case 4:
                        for pos in self.line_search(1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(-1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        for pos in self.line_search(1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                return 1
                        else: 
                            return 0

                    # pawn
                    case 5:
                        # first get direction pawn is moving
                        if piece.color == 0:  # white
                            sign = 1 
                        else:  # black
                            sign = -1 
                        # normal pawn move
                        if move[0][1] == move[1][1]:  # pawns only move forward unless capturing
                            if move[0][0] + sign == move[1][0]:  # check for piece infront of pawn
                                if not piece2:  # valid move
                                    return 1
                                else:
                                    return 0
                            elif move[0][0] + 2*sign == move[1][0] and not piece.get_moved(): # valid move
                                if not piece2:
                                    if not self.grid[move[0][0]+sign][move[0][1]]:
                                        return 1
                                    else: return 0
                                else: return 0
                            else:  # invalid move
                                return 0
                        # capturing pawn move
                        elif move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]: # attempted capture
                            # make sure move is diagonal
                            if move[0][0] + sign != move[1][0]:  # invalid move
                                return 0
                            # En Passant
                            elif self.grid[move[1][0]][move[1][1]] == 0:  # no piece forward-diagonal from pawn
                                # en passant requirements: pawn left or right of current pawn
                                # that pawn has enpassant flag (just made first move of two squares)
                                # check square:[row move0][col move1] for en passantable pawn
                                pawn2 = self.grid[move[0][0]][move[1][1]]
                                if pawn2 != 0:  # en pesant?
                                    if pawn2.get_enpassant():  # yes en pesant
                                        if set_enpassant:
                                            self.set_someone_attempting_enpassant_move(True)
                                        return 1
                                    else:  # no en pesant
                                        return 0
                                else: 
                                    return 0
                            elif self.grid[move[1][0]][move[1][1]] != 0:  # valid capture
                                return 1

                        else:  # invalid move
                                return 0
                    
                    case _:  # invalid piece id
                        return 0
                    
            else:  # moving piece of wrong color
                return 0
        else:  # not piece
            return 0
        

    # function to reset enpassant for all pawns (also all pieces but only pawns matter)
    def unenpassant(self, color):
        
        if color:
            pcs = self.b_pcs
        else:
            pcs = self.w_pcs
        for piece in pcs:
            if piece.enpassant:
                piece.set_enpassant(0)


    # function to check if king is attacked after applying a move
    def king_safety(self, opp_color):

        self.attacked_squares(opp_color)
        # opp_color is color of pieces to check attacked squares of
        # => not opp_color is color of king of which safety is being checked for
        if opp_color:  # opp_color = black
            king_pos = self.w_coords[0]
            if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_b):
                return 0
            else:
                return 1
        else:  # opp_color = white
            king_pos = self.b_coords[0]
            if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_w):
                return 0
            else:
                return 1


    # function to apply move
    def apply_move(self, move, color):
        
        piece = self.grid[move[0][0]][move[0][1]]
        piece.set_moved(True)
        # castling
        if self.get_castle_kingside():
            if color:  # black to move
                # king on e8, hasn't moved
                rook = self.grid[7][7]  # black h rook, hasn't moved
                self.grid[7][6] = piece
                self.grid[7][5] = rook
                self.grid[7][4] = 0  # don't forget to remove old reference to king
                self.grid[7][7] = 0  # and the old reference to the rook
                self.b_coords[piece.id] = [7,6]
                self.b_coords[rook.id] = [7,5]
                rook.set_moved(True)
            else: # white to move
                # king on e1, hasn't moved
                rook = self.grid[0][7]  # white h rook, hasn't moved
                self.grid[0][6] = piece
                self.grid[0][5] = rook
                self.grid[0][4] = 0
                self.grid[0][7] = 0
                self.w_coords[piece.id] = [0,6]
                self.w_coords[rook.id] = [0,5]
                rook.set_moved(True)
            self.set_castle_kingside(0)
        elif self.get_castle_queenside():
            if color: # black to move
                # king on e8, hasn't moved
                rook = self.grid[7][0]  # black a rook, hasn't moved
                self.grid[7][2] = piece
                self.grid[7][3] = rook
                self.grid[7][4] = 0
                self.grid[7][0] = 0 
                self.b_coords[piece.id] = [7,2]
                self.b_coords[rook.id] = [7,3]
                rook.set_moved(True)
            else: # white to move
                # king on e1, hasn't moved
                rook = self.grid[0][0]  # white a rook, hasn't moved
                self.grid[0][2] = piece
                self.grid[0][3] = rook
                self.grid[0][4] = 0
                self.grid[0][0] = 0  # ARGGGGGGGGGGGGGGGGG!!!!!!!!!!!!!!!!!! ;-;^10^10^10^10
                self.w_coords[piece.id] = [0,2]
                self.w_coords[rook.id] = [0,3]
                rook.set_moved(True)
            self.set_castle_queenside(0)
        # en passant
        elif self.get_someone_attempting_enpassant_move():
            if color:  # black en passanting white
                sign = 1
                cap_coords = self.w_coords
                self.b_coords[piece.id] = move[1]
            else:  # white en passanting black
                sign = -1
                cap_coords = self.b_coords
                self.w_coords[piece.id] = move[1]
            # direction (kingside/queenside) pawn to capture is on is contained in move[1][1]
            pawn2 = self.grid[move[1][0] + sign][move[1][1]]
            # remove en passanted pawn
            pawn2.set_captured(1)
            self.grid[move[1][0] + sign][move[1][1]] = 0
            cap_coords[pawn2.id] = [-1,-1]
            if sign:  # black en passanting white => white pawn captured
                self.material_w[pawn2.id] = 0
            else:  # white en passanting black => black pawn captured
                self.material_b[pawn2.id] = 0
            # update grid
            self.grid[move[1][0]][move[1][1]] = piece
            self.grid[move[0][0]][move[0][1]] = 0
            self.set_someone_attempting_enpassant_move(False)
        # normal move
        else:
            piece2 = self.grid[move[1][0]][move[1][1]]
            self.grid[move[1][0]][move[1][1]] = piece
            self.grid[move[0][0]][move[0][1]] = 0
            if color:  # color = black
                self.b_coords[piece.id] = move[1]
                if piece2 != 0:
                    piece2.set_captured(1)
                    self.w_coords[piece2.id] = [-1,-1]
                    self.material_w[piece2.id] = 0
            else:  # color = white
                self.w_coords[piece.id] = move[1]
                if piece2 != 0:
                    piece2.set_captured(1)
                    self.b_coords[piece2.id] = [-1,-1]
                    self.material_b[piece2.id] = 0
        # check if pawn moved 2 squares and set it's en passant flag
        # also check if pawn has reach the opponents back rank and make it a queen
        if piece.type == 5:
            if color:
                sign = -2
                rank = 0
            else:
                sign = 2
                rank = 7
            if move[0][0] + sign == move[1][0] and move[0][1] == move[1][1]:
                piece.set_enpassant(1)
            elif move[1][0] == rank: # pawn has reached opponent's back rank
                piece.make_queen()
                self.set_queening(piece)


    # function to add boardstate to history list to check for threefold repetition
    def update_history(self, move=None):
        lst = []
        for row in range(8):
            for col in range(8):
                p = self.grid[row][col]
                if p != 0:
                    # 0-15: white; 16-31: black
                    lst.append(p.id + 16*p.color)
                else: lst.append(-1)  # -1=no piece
        self.board_history.append(lst)
        if move:
            self.move_history.append(move)
            print(f"grid: updated history with move {move}, new history: {self.move_history}")


    # function to check for a threefold repetition => draw
    def check_threefold(self):
        
        cnt = 0
        curr = self.board_history[-1]
        for lst in self.board_history:
            if lst == curr:
                cnt += 1
        if cnt == 3:
            return 1
        return 0
    

    # function to check if king of color is mated or stalemated
    # returns tuple (color that ended game, x) where x = 0 for checkmate, x = 1 for stalemate
    # returns (-1, -1) if game not ended yet
    def check_mate(self, color):
        # color = side that just moved => about to be not color's turn
        # not color might be check mated or in stalemate
        # need to check if not color's king is in color's attacked squares
        self.attacked_squares(not color, validation=1)  # get not color's available moves
        # checking if black is checkmating/stalemating white
        if color: 
            if len(self.valid_moves_w) == 0:
                self.attacked_squares(color)
                king_pos = self.w_coords[0]
                if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_b):
                    # white has no moves and is in check => checkmate
                    return (1,0)
                else:
                    # white has no moves and is not in check => stalemate
                    return (1,1)
            else: return (-1,-1)
        # checking if white is checkmating/stalemating black
        else:
            if len(self.valid_moves_b) == 0:
                self.attacked_squares(color)
                king_pos = self.b_coords[0]
                if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_w):
                    # black has no moves and is in check => checkmate
                    return (0,0)
                else:
                    # black has no moves and is not in check => stalemate
                    return (0,1)
            else: return (-1,-1)


    # function to add valid moves to valid_lst for color iff move is valid
    def update_validmoves_lst(self, move, color, valid_lst):
        if self.valid_move(move, color):
            tmp_board = copy.deepcopy(self)
            tmp_board.apply_move(move, color)
            # check opponents attacked squares for check
            if(tmp_board.king_safety(not color)):
                # create copy of move to avoid reference issues
                move_copy = copy.deepcopy(move)
                valid_lst.append(move_copy)
            tmp_board = None  # remove reference for garbage collection

    
    # method to caulculate material difference
    def material_count(self):
        self.material_diff = np.sum(self.material_w) - np.sum(self.material_b)

    
    # method to set all pieces to not moved (for history boards)
    def set_unmoved(self):
        for piece in self.w_pcs:
            piece.set_moved(False)
        for piece in self.b_pcs:
            piece.set_moved(False)


    # method to set grid according to coordinates (for history boards)
    def set_grid(self, white, black):
        for n in range(8):
            for m in range(8):
                self.grid[n][m] = 0
        type_mapping = {0:0, 1:1, 2:2, 3:2, 4:3, 5:3, 6:4, 7:4, 
                        8:5, 9:5, 10:5, 11:5, 12:5, 13:5, 14:5, 15:5}
        for index, coord in enumerate(white):
            self.grid[coord[0]][coord[1]] = Piece(0, type_mapping[index], index)
        for index, coord in enumerate(black):
            self.grid[coord[0]][coord[1]] = Piece(1, type_mapping[index], index)