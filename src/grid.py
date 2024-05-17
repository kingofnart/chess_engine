import numpy as np
import copy
from piece import Piece

class Grid():
    
    def __init__(self):
        # color key: 0 = white, 1 = black
        self.names = {0: "White", 1: "Black"}
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
        # initialize lists
        self.board_history = []
        self.attacked_squares_w = []
        self.attacked_squares_b = []
        self.valid_moves_w = []
        self.valid_moves_b = []
        # special move flags
        self.someone_attempting_enpassant_move = False
        self.castle_queenside = 0
        self.castle_kingside = 0
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
    # setters
    def set_someone_attempting_enpassant_move(self, input):
       self.someone_attempting_enpassant_move = input
    def set_castle_kingside(self, input):
        self.castle_kingside = input
    def set_castle_queenside(self, input):
        self.castle_queenside = input

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
        self.enspassant = 0
        self.castle_queenside = 0
        self.castle_kingside = 0
        self.board_history = []
        self.valid_moves_w = self.attacked_squares(0, validation=1) # also sets attacked_squares_w
        self.valid_moves_b = self.attacked_squares(1, validation=1) # also sets attacked_squares_b
    
    # function to save list of all squares attacked by a color
    # validation flag is if you want to store all valid moves
    # don't want to validate if im checking attacked squares on tmp grid for king safety
    def attacked_squares(self, color, validation=0):
        attacked_list = []
        # get references to correct lists
        if color:
            self.attacked_squares_b = []
            attacked_list = self.attacked_squares_b
            pieces = self.b_pcs
            coords = self.b_coords
        else:
            self.attacked_squares_w = []
            attacked_list = self.attacked_squares_w
            pieces = self.w_pcs
            coords = self.w_coords
        if validation:
            # print("finding all valid moves for {}".format(self.names[color]))
            if color:  # black
                self.valid_moves_b = []
                valid_moves = self.valid_moves_b
            else:  # white
                self.valid_moves_w = []
                valid_moves = self.valid_moves_w
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
                        lst = self.line_search(0, 1, coord, get_valid=validation)  # 0
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 1, coord, get_valid=validation)  # pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 0, coord, get_valid=validation)  # pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, -1, coord, get_valid=validation)  # 3pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(0, -1, coord, get_valid=validation)  # pi
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, -1, coord, get_valid=validation)  # 5pi/4
                        self.add_to_list(attacked_list, lst) 
                        lst = self.line_search(-1, 0, coord, get_valid=validation)  # 3pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 1, coord, get_valid=validation)  # 7pi/4
                        self.add_to_list(attacked_list, lst)

                    # rook
                    case 2:
                        # only horizontals & verticals
                        lst = self.line_search(0, 1, coord, get_valid=validation)  # 0
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, 0, coord, get_valid=validation)  # pi/2
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(0, -1, coord, get_valid=validation)  # pi
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 0, coord, get_valid=validation)  # 3pi/2
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
                        lst = self.line_search(1, 1, coord, get_valid=validation)  # pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(1, -1, coord, get_valid=validation)  # 3pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, -1, coord, get_valid=validation)  # 5pi/4
                        self.add_to_list(attacked_list, lst)
                        lst = self.line_search(-1, 1, coord, get_valid=validation)  # 7pi/4
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
                                # print("validating queenside pawn capture for {}'s {} pawn".format(self.names[color], piece.id))
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
        # just for debugging
        # if validation:
        #     if color:
        #         print("Updated black's valid move list. Number of valid moves: {}, moves: {}"
        #               .format(len(self.valid_moves_b), self.valid_moves_b))
        #     else:
        #         print("Updated white's valid move list. Number of valid moves: {}, moves: {}"
        #               .format(len(self.valid_moves_w), self.valid_moves_w))

    # helper function for attacked_squares to add each element of list only if it's unique
    # might want to change attacked_squares to set of tuples instead of list of lists
    def add_to_list(self, old, new):
        if len(new) > 0:
            for x in new:
                if x not in old:
                    old.append(x)

    # helper function for attacked_squares to search along vert/hor/diag lines
    # for queen, rook, bishop
    def line_search(self, y, x, coord, get_valid = False): # x, y = -1,0,1 to set search direction
        search = True
        lst = []
        # don't set square piece is on to attacked, piece cant attack itself!
        idx = [coord[0] + y, coord[1] + x] 
        # want to search in straight line until you find piece or edge of board
        while idx[0] <= 7 and idx[0] >= 0 and idx[1] <= 7 and idx[1] >= 0 and search:
            lst.append(idx.copy())
            if get_valid:
                # print("Getting valid moves in linesearch")
                color = self.grid[coord[0]][coord[1]].color
                if color:
                    self.update_validmoves_lst([coord.tolist(), idx], color, self.valid_moves_b)
                else:
                    self.update_validmoves_lst([coord.tolist(), idx], color, self.valid_moves_w)
            if self.grid[idx[0]][idx[1]] != 0:  # found piece, stop search
                search = False
            idx[0] = idx[0] + y
            idx[1] = idx[1] + x
        return lst
    
    # function to test if move is valid
    def valid_move(self, move, color, flag=0):
        
        # move = [[x1, y1], [x2, y2]]
        piece = self.grid[move[0][0]][move[0][1]]
        if piece:
            #  print("Checking if moving piece (id,color): ({},{}) from [{},{}] to [{},{}] is valid..."
            #       .format(piece.id, piece.color, move[0][0], move[0][1], move[1][0], move[1][1]))
            # check to make sure you're moving the right color piece
            if piece.color == color:
                # make sure you're not capturing your own piece
                piece2 = self.grid[move[1][0]][move[1][1]]
                if piece2:
                    if piece2.color == color:
                        #print("Can't capture your own piece. Invalid move. Not applying...")
                        return 0
                    #print("Making a capture, piece capturing (id,color):", piece2.id, piece2.color)
                
                match piece.type:
                    
                    # king
                    case 0:
                        dif1 = np.abs(move[0][0] - move[1][0])
                        dif2 = np.abs(move[0][1] - move[1][1])
                        # normal king move
                        if dif1 <= 1 and dif2 <= 1:
                            if move[1][0] >= 0 and move[1][0] <= 7 and move[1][1] >= 0 and move[1][1] <= 7:
                                #print("Valid king move. Applying...")
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
                                #print("Pieces in between king and rook. Invalid move. Not applying...")
                                return 0
                            if color:
                                atck_lst = self.attacked_squares_w
                                # check black h rook and king haven't moved yet
                                if self.b_pcs[3].get_moved() or piece.get_moved():
                                    #print("Can't castle after moving. Invalid move. Not applying...")
                                    return 0
                            else:
                                atck_lst = self.attacked_squares_b
                                # check white h rook and king haven't moved yet
                                if self.w_pcs[3].get_moved() or piece.get_moved():
                                    #print("Can't castle after moving. Invalid move. Not applying...")
                                    return 0
                            # cant castle through, out of, or into check
                            for pos in atck_lst:
                                if move[0][0] == pos[0] and move[0][1] == pos[1]:
                                    #print("Can't castle while in check. Invalid move. Not applying...")
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] + 1 == pos[1]:
                                    #print("Can't castle through check. Invalid move. Not applying...")
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] + 2 == pos[1]:
                                    #print("Can't castle into check. Invalid move. Not applying...")
                                    return 0
                            #print("Valid king side castle move. Applying...")
                            self.castle_kingside = 1
                            return 1
                        elif move[0][1] - 2 == move[1][1]:  # caslting queenside
                            # make sure squares between king and rook are empty
                            if self.grid[move[0][0]][move[0][1] - 1] != 0 or self.grid[move[0][0]][move[0][1] - 2] != 0 \
                                or self.grid[move[0][0]][move[0][1] - 3] != 0:
                                #print("Pieces in between king and rook. Invalid move. Not applying...")
                                return 0
                            if color:
                                atck_lst = self.attacked_squares_w
                                # check black a rook and king haven't moved yet
                                if self.b_pcs[2].get_moved() or piece.get_moved():
                                    #print("Can't castle after moving. Invalid move. Not applying...")
                                    return 0
                            else:
                                atck_lst = self.attacked_squares_b
                                # check white a rook and king haven't moved yet
                                if self.w_pcs[2].get_moved() or piece.get_moved():
                                    #print("Can't castle after moving. Invalid move. Not applying...")
                                    return 0
                            # cant castle through, out of, or into check
                            for pos in atck_lst:
                                if move[0][0] == pos[0] and move[0][1] == pos[1]:
                                    #print("Can't castle while in check. Invalid move. Not applying...")
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] - 1 == pos[1]:
                                    #print("Can't castle through check. Invalid move. Not applying...")
                                    return 0
                                elif move[0][0] == pos[0] and move[0][1] - 2 == pos[1]:
                                    #print("Can't castle into check. Invalid move. Not applying...")
                                    return 0
                            #print("Valid queenside castle move. Applying...")
                            self.castle_queenside = 1
                            return 1
                        #print("Invalid king move. Not applying...")
                        return 0

                    # queen
                    case 1: 
                        for pos in self.line_search(1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(0, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(-1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(-1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(-1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(0, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        for pos in self.line_search(1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid queen move. Applying...")
                                return 1
                        else: 
                            #print("Invalid queen move. Not applying...")
                            return 0

                    # rook
                    case 2:
                        for pos in self.line_search(1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid rook move. Applying...")
                                return 1
                        for pos in self.line_search(0, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid rook move. Applying...")
                                return 1
                        for pos in self.line_search(-1, 0, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid rook move. Applying...")
                                return 1
                        for pos in self.line_search(0, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid rook move. Applying...")
                                return 1
                        else: 
                            #print("Invalid rook move. Not applying...")
                            return 0

                    # knight
                    case 3:
                        if move[0][0] + 2 == move[1][0] or move[0][0] - 2 == move[1][0]:
                            if move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]:
                                #print("Valid knight move. Applying...")
                                return 1
                        elif move[0][1] + 2 == move[1][1] or move[0][1] - 2 == move[1][1]:
                            if move[0][0] + 1 == move[1][0] or move[0][0] - 1 == move[1][0]:
                                #print("Valid knight move. Applying...")
                                return 1
                        else: 
                            #print("Invalid knight move. Not applying...")
                            return 0

                    # bishop
                    case 4:
                        for pos in self.line_search(1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid bishop move. Applying...")
                                return 1
                        for pos in self.line_search(-1, 1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid bishop move. Applying...")
                                return 1
                        for pos in self.line_search(-1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid bishop move. Applying...")
                                return 1
                        for pos in self.line_search(1, -1, move[0]):
                            if move[1][0] == pos[0] and move[1][1] == pos[1]:
                                #print("Valid bishop move. Applying...")
                                return 1
                        else: 
                            #print("Invalid bishop move. Not applying...")
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
                                    #print("Valid pawn move. Applying...")
                                    return 1
                                else:
                                    #print("Pawns can only capture diagonally. Invalid move. Not applying...")
                                    return 0
                            elif move[0][0] + 2*sign == move[1][0] and not piece.get_moved(): # valid move
                                if not piece2:
                                    #print("Valid pawn move. Applying...")
                                    return 1
                                else:
                                    #print("Pawns can only capture diagonally. Invalid move. Not applying...")
                                    return 0
                            else:  # invalid move
                                #print("Invalid pawn move! Not applying...")
                                return 0
                        # capturing pawn move
                        elif move[0][1] + 1 == move[1][1] or move[0][1] - 1 == move[1][1]: # attempted capture
                            # make sure move is diagonal
                            if move[0][0] + sign != move[1][0]:  # invalid move
                                #print("Invalid pawn move. Not applying...")
                                return 0
                            # En Passant
                            elif self.grid[move[1][0]][move[1][1]] == 0:  # no piece forward-diagonal from pawn
                                # en passant requirements: pawn left or right of current pawn
                                # that pawn has enpassant flag (just made first move of two squares)
                                # check square:[row move0][col move1] for en passantable pawn
                                pawn2 = self.grid[move[0][0]][move[1][1]]
                                if pawn2 != 0:  # en pesant?
                                    if pawn2.get_enpassant():  # yes en pesant
                                        #print("Valid pawn en passant. Applying...")
                                        if flag:
                                            # print("SETTING EN PASSANT!!!!!!!!")
                                            self.set_someone_attempting_enpassant_move(True)
                                        return 1
                                    else:  # no en pesant
                                        #  print("En passant cannot be perfomed on piece at [{},{}]. Invalid move. Not applying..."
                                        #       .format(move[0][0], move[1][1]))
                                        return 0
                                else: 
                                     #print("Invalid capture attempt. Not applying...")
                                    return 0
                            elif self.grid[move[1][0]][move[1][1]] != 0:  # valid capture
                                 #print("Valid pawn move. Applying...")
                                return 1

                        else:  # invalid move
                                 #print("Invalid pawn move. Not applying...")
                                return 0
                    
                    case _:  # invalid piece id
                        return 0
                    
            else:  # moving piece of wrong color
                 #print("Wrong color, move a piece of the other color. Not applying...")
                return 0
        else:  # not piece
             #print("Invalid move, must select piece. Not applying...")
            return 0
        
    # function to reset enpassant for all pawns (also all pieces but only pawns matter)
    def unenpassant(self, color):
        if color:
            pcs = self.b_pcs
        else:
            pcs = self.w_pcs
        for piece in pcs:
            if piece.enpassant:
                # print("Pawn ", piece.id, " of color ", piece.color, " has be unenpassanted.")
                piece.set_enpassant(0)

    # function to check if king is attacked after applying a move
    def king_safety(self, opp_color):
        self.attacked_squares(opp_color)
        # color is color of pieces to check attacked squares of
        if opp_color:  # opp_color = black
            king_pos = self.w_coords[0]
            if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_b):
                # print("White king is put in check by that move. Invalid move. Not applying...")
                return 0
            else:
                 #print("Move retains king safety. Valid move. Applying...")
                return 1
        else:  # opp_color = white
            king_pos = self.b_coords[0]
            if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_w):
                # print("Black king is put in check by that move! Invalid, not applying...")
                return 0
            else:
                 #print("Move retains king safety. Valid move. Applying...")
                return 1
            
    # function to apply move
    def apply_move(self, move, color):
        piece = self.grid[move[0][0]][move[0][1]]
        #print("Moving piece (id,color): ", piece.id, piece.color)
        piece.set_moved(True)
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
                self.grid[7][7] = 0
                self.b_coords[piece.id] = [7,2]
                self.b_coords[rook.id] = [7,3]
            else: # white to move
                # king on e1, hasn't moved
                rook = self.grid[0][7]  # white a rook, hasn't moved
                self.grid[0][2] = piece
                self.grid[0][3] = rook
                self.grid[0][4] = 0
                self.grid[0][7] = 0
                self.w_coords[piece.id] = [0,2]
                self.w_coords[rook.id] = [0,3]
            rook.set_moved(True)
            self.set_castle_queenside(0)
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
            # update grid
            self.grid[move[1][0]][move[1][1]] = piece
            self.grid[move[0][0]][move[0][1]] = 0
            self.set_someone_attempting_enpassant_move(False)
            # print("An en passant has taken place! ****!")
        else:
            piece2 = self.grid[move[1][0]][move[1][1]]
            self.grid[move[1][0]][move[1][1]] = piece
            self.grid[move[0][0]][move[0][1]] = 0
            if color:  # color = black
                self.b_coords[piece.id] = move[1]
                if piece2 != 0:
                    #print("Capturing white piece (id,color): ", piece2.id, piece2.color)
                    piece2.set_captured(1)
                    self.w_coords[piece2.id] = [-1,-1]
            else:  # color = white
                self.w_coords[piece.id] = move[1]
                if piece2 != 0:
                    #print("Capturing black piece (id,color): ", piece2.id, piece2.color)
                    piece2.set_captured(1)
                    self.b_coords[piece2.id] = [-1,-1]
        # finally check if pawn moved 2 squares and set it's en passant flag
        if color:
            sign = -2
        else: sign = 2
        if piece.type == 5 and move[0][0] + sign == move[1][0] and move[0][1] == move[1][1]:
            piece.set_enpassant(1)
            # print("Pawn ({},{}) can now be en passanted".format(piece.id, piece.color))

    # function to add boardstate to history list to check for threefold repetition
    def update_history(self):
        lst = []
        for row in range(8):
            for col in range(8):
                p = self.grid[row][col]
                if p != 0:
                    # 0-15: white; 16-31: black
                    lst.append(p.id + 16*p.color)
                else: lst.append(-1)
        self.board_history.append(lst)

    # function to check for a threefold repetition => draw
    def check_threefold(self):
        cnt = 0
        curr = self.board_history[-1]
        for lst in self.board_history:
            if lst == curr:
                cnt += 1
        if cnt == 3:
            print("Threefold repetition reached. It's a draw, game over.")
            return 1
        return 0
    
    # function to check if king is mated or stalemated
    def check_mate(self, color):
        # color = side that just moved => about to be not color's turn
        # not color might be check mated or in stalemate
        # need to check if not color's king is in color's attacked squares
        self.attacked_squares(not color, validation=1)  # get not color's available moves
        # checking if black is checkmating white
        if color: 
            if len(self.valid_moves_w) == 0:
                self.attacked_squares(color)
                king_pos = self.w_coords[0]
                if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_b):
                    # white has no moves and is in check => checkmate
                    print("Black has checkmated White. Black wins. Game over.")
                    return 1
                else:
                    # white has no moves and is not in check => stalemate
                    print("Black has stalemated White. It's a draw. Game over.")
                    return 1
            else: return 0
        # checking if white is checkmating black
        else: 
            if len(self.valid_moves_b) == 0:
                self.attacked_squares(color)
                king_pos = self.b_coords[0]
                if any(king_pos[0] == x[0] and king_pos[1] == x[1] for x in self.attacked_squares_w):
                    # black has no moves and is in check => checkmate
                    print("White has checkmated Black. White wins. Game over.")
                    return 1
                else:
                    # black has no moves and is not in check => stalemate
                    print("White has stalemated Black. It's a draw. Game over.")
                    return 1
            else: return 0

    def update_validmoves_lst(self, move, color, valid_lst):
        if self.valid_move(move, color):
            tmp_board = copy.deepcopy(self)
            #print("Checking move retains king safety...")
            tmp_board.apply_move(move, color)
            # check opponents attacked squares for check
            if(tmp_board.king_safety(not color)):
                # print("Adding move [[{},{}],[{},{}]] to valid moves list {}"
                #       .format(move[0][0], move[0][1], move[1][0], move[1][1], self.names[color]))
                valid_lst.append(move)