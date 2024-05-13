import copy
from grid import Grid

class Game():
    def __init__(self):
        self.board = Grid()
        self.turn = 1 # 1 = white to move, 0 = black to move, opposite of "color"
        while True:
            move = [[0,0],[0,1]] # gui.get_move()
            if self.board.valid_move(move):
                tmp_board = copy.deepcopy(self.board)
                tmp_board.apply_move(move)
                # check opponents attacked squares for check
                if(tmp_board.king_safety(self.turn)):
                    self.board.apply_move(move)
                    self.turn = not self.turn