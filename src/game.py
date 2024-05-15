import copy
from tkinter import *
from grid import Grid
from gui import ChessBoard

class Game():

    def __init__(self):

        self.board = Grid()
        self.turn = 0 # 0 = white, 1 = black

    def play(self):
        print("Game starting! It is white to move.")
        print("-----------------------------------------------------------------")
        root = Tk()
        ChessBoard(root, self.make_move, self.board.w_coords, self.board.b_coords)
        root.mainloop()

    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, sq1, sq2):
        colors = {0: "White", 1: "Black"}
        if self.board.valid_move([sq1, sq2], self.turn):
            tmp_board = copy.deepcopy(self.board)
            print("Checking apply move on tmp board...")
            tmp_board.apply_move([sq1, sq2], self.turn)
            # check opponents attacked squares for check
            if(tmp_board.king_safety(not self.turn)):
                print("King still safe, still applying...")
                self.board.apply_move([sq1, sq2], self.turn)
                self.board.unenpassant(not self.turn)
                self.turn = not self.turn 
                print("Move applied, it is now {}'s turn.".format(colors[self.turn]))
                print("-----------------------------------------------------------------")
        else:
            print("*** Invalid move, try again. ***")
        return self.board.w_coords, self.board.b_coords # to update ChessBoard
