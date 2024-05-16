import copy
from tkinter import *
from grid import Grid
from gui import ChessBoard

class Game():

    def __init__(self):

        self.board = Grid()
        self.turn = 0 # 0 = white, 1 = black
        self.board_history = []
        self.stop = False

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
                self.update_history()
                if self.check_threefold():
                    self.stop = True
                else:
                    print("Move applied, it is now {}'s turn.".format(colors[self.turn]))
                    print("-----------------------------------------------------------------")
        else:
            print("*** Invalid move, try again. ***")
        if self.stop:
            return [420], [69]
        return self.board.w_coords, self.board.b_coords # to update ChessBoard

    # function to add boardstate to history list to check for threefold repetition
    def update_history(self):
        lst = []
        for row in range(8):
            for col in range(8):
                p = self.board.grid[row][col]
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
            print("Threefold reached. It's a draw, game over.")
            return 1
        return 0