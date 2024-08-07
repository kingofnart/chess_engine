import copy
import threading
from grid import Grid
from engine import Engine
from src.chess_app.connect import connect
from flask import current_app
from flask_login import current_user
from datetime import datetime
from tzlocal import get_localzone

class Game():

    def __init__(self, game_id):

        self.lock = threading.Lock()
        self.board = Grid()
        self.engine = Engine(self.board)
        self.turn = 0  # 0 = white, 1 = black
        self.stop = False
        self.save = True
        self.minimax_depth = 3
        self.stop_condition = -1
        self.promotion_info = None
        # stop conditions: 0=white flag, 1=black flag, 2=white checkmate; 
        # 3=white stalemate, 4=black checkmate, 5=black stalemate, 6=threefold
        self.id = game_id


    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, move):
        
        # about to update data structures, acquire lock
        with self.lock:

            if move[0] == "reset":
                return self.reset()
            
            elif move[0] == "save game":
                return self.save_game(self.board.move_history, move[1], move[2])
            
            elif move[0] == "revert":
                print(f"GAME: revert promotion: {move[3]}")
                return self.revert(move[1], move[2], move[3])
            
            else:
                return self.apply_move(move)
            

    def apply_move(self, move):

        # make sure nobody's timer ran out
        if move[0] is None:
            self.stop = True
            if move[1] == 'white':
                self.stop_condition = 0
            else:
                self.stop_condition = 1

        else:  # timers still running
            # check if move is from computer
            if move[0] == "random":
                mv = self.engine.random_move(self.turn)
            elif move[0] == "minimax":
                mv = self.engine.minimax(self.turn, self.minimax_depth)
            # check if move is from history board
            elif 'nothingtoseehere' in move:
                move.pop(2)
                mv = move
                self.save = False
            else: # move from player via handleClick
                # move is in form: ['y1,x1','y2,x2'] => move[0][1]=move[1][1]=','
                mv = [[int(move[0][0]), int(move[0][2])], [int(move[1][0]), int(move[1][2])]]
            
            self.promotion_info = None
            if self.board.valid_move(mv, self.turn, set_enpassant=True):
                tmp_board = copy.deepcopy(self.board)
                tmp_board.apply_move(mv, self.turn)
                # check opponents attacked squares for check
                if not tmp_board.king_safety(not self.turn):
                    # return coords to flash the king thats being put in check
                    if self.turn:
                        ret_coords = self.board.b_coords
                    else:
                        ret_coords = self.board.w_coords
                    if print:
                        print(f"GAME: move puts king in check: {mv}")
                    return {'error': 'king safety', 'coords': ret_coords.tolist()}
                del tmp_board # release memory
                self.board.apply_move(mv, self.turn)
                # need to make a flag to tell frontend if queening is occurring
                
                if self.board.get_queening() is not None:
                    # promotion has piece id as index, color, coordinate
                    if self.turn:  # black queening
                        coords_lst = self.board.b_coords
                    else:  # white queening
                        coords_lst = self.board.w_coords
                    self.promotion_info = {'index': self.board.queening.id, 'color': self.turn, 
                                    'coord': coords_lst[self.board.queening.id].tolist()}
                    self.board.set_queening(None)
                if self.save:
                    self.board.update_history(mv)
                # check stopping conditions
                if self.board.check_threefold():
                    self.stop = True
                    self.stop_condition = 6
                else:
                    # NOTE check_mate is called with color of the side that just made a move
                    # => check_mate checks the length of the valid_moves list for NOT color
                    (p,q) = self.board.check_mate(self.turn)
                    if (p,q) != (-1,-1):
                        if self.save:
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
            else: 
                return {'error': 'invalid'}  # valid_move() failed
        if self.stop:
            # return in json format
            return {
                'status': 'end', 
                'end_result': self.stop_condition,
                'promotion': self.promotion_info
            }
        # proceed with game
        self.turn = 0 if self.turn else 1
        self.board.unenpassant(self.turn)
        self.board.update_material_count()
        return {
            'status': 'move applied',
            'w_coords': self.board.w_coords.tolist(), 
            'b_coords': self.board.b_coords.tolist(),
            'turn': self.turn,
            'promotion': self.promotion_info,
            'material_diff': int(self.board.get_material_diff())
        }


    def reset(self):
        self.turn = 0
        self.stop = False
        self.save = True
        self.stop_condition = -1
        self.board.reset()
        return { 'status': 'reset' }
    

    def save_game(self, history, opponent, color):
        with current_app.app_context():
            if not current_user.is_authenticated:
                return "User not logged in", 401
        history = self.to_native(history)
        local_tz = get_localzone() # get local machines timzone
        game_time = datetime.now(local_tz).replace(second=0, microsecond=0)
        conn = connect()
        if conn == -1:
            return "Error connecting to database", 500
        with conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO games (user_id, game_history, game_time, opponent, color) VALUES (%s, %s, %s, %s, %s)", 
                            (current_user.id, history, game_time, opponent, color))
                conn.commit()
        return { 'status': 'game saved' }
    

    def revert(self, new_w_coords, new_b_coords, promoted):
        self.stop = False
        self.stop_condition = -1
        self.turn = not self.turn
        self.board.undo_move(new_w_coords, new_b_coords)
        if promoted is not None:
            print(f"GAME: revert not None; promotion: {promoted}")
            self.board.undo_queen(promoted[0], promoted[1])
        return {
            'status': 'move applied',
            'w_coords': self.board.w_coords.tolist(),
            'b_coords': self.board.b_coords.tolist()
        }
    

    # need at least two endpoints for Flask
    # function to send game state to frontend
    def get_state(self):
        with self.lock:
            return {
                'w_coords': self.board.w_coords.tolist(),
                'b_coords': self.board.b_coords.tolist(),
                'history': self.board.board_history
            }


    def to_native(self, value):
        if isinstance(value, list):
            return [self.to_native(item) for item in value]
        elif not isinstance(value, int):
            return int(value)
        return value