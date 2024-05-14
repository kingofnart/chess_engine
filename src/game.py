import copy
from tkinter import *
from grid import Grid
from gui import ChessBoard

class Game():

    def __init__(self):

        self.board = Grid()
        self.turn = 0 # 0 = white, 1 = black

    def play(self):
        while True:
            root = Tk()
            ChessBoard(root, self.make_move, self.board.w_coords, self.board.b_coords)
            root.mainloop()

    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, sq1, sq2):
        if self.board.valid_move([sq1, sq2]):
            tmp_board = copy.deepcopy(self.board)
            tmp_board.apply_move([sq1, sq2], self.turn)
            # check opponents attacked squares for check
            if(tmp_board.king_safety(self.turn)):
                self.board.apply_move([sq1, sq2], self.turn)
                self.turn = not self.turn 
        return self.board.w_coords, self.board.b_coords # to update ChessBoard
