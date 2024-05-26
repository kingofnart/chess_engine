import copy
from tkinter import *
from grid import Grid

class Game():


    def __init__(self):

        self.board = Grid()
        self.turn = 0  # 0 = white, 1 = black
        self.board_history = []
        self.stop = False
        self.stop_condition = -1
        # stop conditions: 0=white flag, 1=black flag, 2=white checkmate; 
        # 3=white stalemate, 4=black checkmate, 5=black stalemate, 6=threefold
        

    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, move):
        # first make sure nobody's timer ran out
        if move[0] is None:
            self.stop = True
            if move[1] == 'white':
                self.stop_condition = 0
            else:
                self.stop_condition = 1
        else:  # timers still running
            sq1 = [int(move[0][0]), int(move[0][2])]
            sq2 = [int(move[1][0]), int(move[1][2])]
            colors = {0: "White", 1: "Black"}
            if self.board.valid_move([sq1, sq2], self.turn, set_enpassant=True):
                tmp_board = copy.deepcopy(self.board)
                tmp_board.apply_move([sq1, sq2], self.turn)
                # check opponents attacked squares for check
                if not tmp_board.king_safety(not self.turn):
                    # return in json format
                    if self.turn:
                        ret_coords = self.board.b_coords
                    else:
                        ret_coords = self.board.w_coords
                    return {'error': 'king safety', 'coords': ret_coords.tolist()}
                self.board.apply_move([sq1, sq2], self.turn)
                # need to make a flag to tell frontend if queening is occurring
                promotion_info = None
                if self.board.get_queening() is not None:
                    # promotion has piece id as index, color, coordinate
                    if self.turn:  # black queening
                        coords_lst = self.board.w_coords
                    else:  # white queening
                        coords_lst = self.board.w_coords
                    promotion_info = {'index': self.board.queening.id, 'color': self.turn, 
                                    'coord': coords_lst[self.board.queening.id].tolist()}
                    self.board.set_queening(None)
                self.board.update_history()
                print("History updated.")
                # check stopping conditions
                if self.board.check_threefold():
                    self.stop = True
                    self.stop_condition = 6
                else:
                    # NOTE check_mate is called with color of the side that just made a move
                    # => check_mate checks the length of the valid_moves list for NOT color
                    (p,q) = self.board.check_mate(self.turn)
                    if (p,q) != (-1,-1):
                        self.stop = True
                        if p:  # black ended game
                            if q:  # black stalemated white
                                self.stop_condition = 5
                            else:  # black checkmate
                                self.stop_condition = 4
                        elif q:  # white stalemated black
                            self.stop_condition = 3
                        else:  # white checkmate
                            self.stop_condition = 2
            else: return {'error': 'invalid'}
        if self.stop:
            # return in json format
            return {
                'status': 'end', 
                'end_result': self.stop_condition
            }
        # proceed with game
        self.turn = not self.turn
        self.board.unenpassant(self.turn)
        print("It is now {}'s turn.".format(colors[self.turn]))
        print("-----------------------------------------------------------------")
        return {
            'status': 'move applied',
            'w_coords': self.board.w_coords.tolist(), 
            'b_coords': self.board.b_coords.tolist(),
            'turn': self.turn,
            'promotion': promotion_info
        }


    # need at least two endpoints for Flask
    # function to send game state to frontend
    def get_state(self):
        return {
            'w_coords': self.board.w_coords.tolist(),
            'b_coords': self.board.b_coords.tolist(),
            'history': self.board_history
        }