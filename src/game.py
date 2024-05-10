import numpy as np
import copy
from grid import Grid

class Game():
    def __init__(self):
        self.board = Grid()
        self.turn = 1 # 1 = white to move, 0 = black to move, opposite of "color"
        while True:
            move = [[0,0],[0,1]] # gui.get_move()
            if self.board.valid_move(move):
                tmp = copy.deepcopy(self.board)
                tmp.board.apply_move(move)
                # check other opponents attacked squares for check
                if(tmp.king_safety(self.turn)):
                    self.board.apply_move(move)
                    self.turn = not self.turn