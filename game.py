import copy
import threading
from grid import Grid
from engine import Engine
from connect import connect
from flask import current_app
from flask_login import current_user
from datetime import datetime
from tzlocal import get_localzone

class Game():

    def __init__(self, game_id, printing=False):

        self.lock = threading.Lock()
        self.board = Grid()
        self.engine = Engine(self.board)
        self.turn = 0  # 0 = white, 1 = black
        self.stop = False
        self.save = True
        self.stop_condition = -1
        self.promotion_info = None
        # stop conditions: 0=white flag, 1=black flag, 2=white checkmate; 
        # 3=white stalemate, 4=black checkmate, 5=black stalemate, 6=threefold
        self.id = game_id
        self.printing = printing


    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, move):
        
        # about to update data structures, acquire lock
        with self.lock:

            if self.printing:
                print(f"GAME {self.id}: recieved {move} from frontend. It is color {self.turn}'s turn.")
            
            if move[0] == "reset":
                return self.reset()
            
            elif move[0] == "save game":
                return self.save_game(self.board.move_history, move[1], move[2])
            
            elif move[0] == "revert":
                return self.revert(move[1], move[2])
            
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
                if self.printing:
                    print(f"GAME: random move: {mv}")
            # check if move is from history board
            elif 'nothingtoseehere' in move:
                move.pop(2)
                mv = move
                if self.printing:
                    print(f"GAME: history move: {mv}")
                self.save = False
            else: # move from player via handleClick
                # move is in form: ['y1,x1','y2,x2'] => move[0][1]=move[1][1]=','
                mv = [[int(move[0][0]), int(move[0][2])], [int(move[1][0]), int(move[1][2])]]
                if self.printing:
                    print(f"GAME: player move: {mv}, calling valid_move with color {self.turn}...")
            
            self.promotion_info = None
            if self.board.valid_move(mv, self.turn, set_enpassant=True, printing=self.printing):
                if self.printing:
                    print(f"GAME: move is valid, checking king safety...")
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
                tmp_board = None
                self.board.apply_move(mv, self.turn)
                # need to make a flag to tell frontend if queening is occurring
                
                if self.board.get_queening() is not None:
                    if self.printing:
                        print(f"GAME: queening detected")
                    # promotion has piece id as index, color, coordinate
                    if self.turn:  # black queening
                        coords_lst = self.board.w_coords
                    else:  # white queening
                        coords_lst = self.board.w_coords
                    self.promotion_info = {'index': self.board.queening.id, 'color': self.turn, 
                                    'coord': coords_lst[self.board.queening.id].tolist()}
                    self.board.set_queening(None)
                if self.save:
                    if self.printing:
                        print(f"GAME: updating history with {mv}")
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
                if self.printing:
                    print(f"GAME: invalid move")
                return {'error': 'invalid'}  # valid_move() failed
        if self.stop:
            # return in json format
            if self.printing:
                print(f"GAME: game over, stop condition: {self.stop_condition}")
            return {
                'status': 'end', 
                'end_result': self.stop_condition,
                'promotion': self.promotion_info
            }
        # proceed with game
        if self.printing:
            print(f"GAME: color {self.turn} has made their move")
        self.turn = 0 if self.turn else 1
        if self.printing:
            print(f"GAME: it is now color {self.turn}'s turn")
        self.board.unenpassant(self.turn)
        self.board.material_count()
        if self.printing:
            print(f"GAME: move applied, updated coordinates:")
            self.print_board()
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
        if self.printing:
            print(f"GAME {self.id}: board reset. Turn: {self.turn}")
            self.print_board()
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
                if self.printing:
                    print(f"GAME: saving move history {history}")
                cur.execute("INSERT INTO games (user_id, game_history, game_time, opponent, color) VALUES (%s, %s, %s, %s, %s)", 
                            (current_user.id, history, game_time, opponent, color))
                conn.commit()
        return { 'status': 'game saved' }
    

    def revert(self, new_w_coords, new_b_coords):
        self.stop = False
        self.stop_condition = -1
        self.turn = not self.turn
        # want to reset moved flag so pawns can move 2 squares
        self.board.set_unmoved()
        self.board.set_white_coords(new_w_coords)
        self.board.set_black_coords(new_b_coords)
        self.board.set_grid(self.board.w_coords, self.board.b_coords)
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


    # for debugging
    def print_board(self):
        white = self.board.w_coords.tolist()
        black = self.board.b_coords.tolist()
        for i in range(8):
            for j in range(8):
                if [i,j] in white:
                    print("w", end="|")
                elif [i,j] in black:
                    print("b", end="|")
                else:
                    print("0", end="|")
            print()