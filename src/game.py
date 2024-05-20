import copy
from tkinter import *
from grid import Grid
from gui import ChessBoard

class Game():

    def __init__(self):

        self.board = Grid()
        self.root = Tk()
        self.gui_board = ChessBoard(self.root, self.make_move, self.endgame, self.board.w_coords, self.board.b_coords)
        self.turn = 0  # 0 = white, 1 = black
        self.board_history = []
        self.stop = False

    def play(self):

        print("Game starting! It is white to move.")
        print("-----------------------------------------------------------------")
        self.gui_board.white_timer.toggle()
        self.root.mainloop()
        

    # ChessBoard class will call this when it gets two clicks input
    def make_move(self, sq1, sq2):

        colors = {0: "White", 1: "Black"}
        if self.board.valid_move([sq1, sq2], self.turn, flag=True):
            tmp_board = copy.deepcopy(self.board)
            print("Checking apply move on tmp board...")
            tmp_board.apply_move([sq1, sq2], self.turn)
            # check opponents attacked squares for check
            if(tmp_board.king_safety(not self.turn)):
                print("King still safe, still applying...")
                self.board.apply_move([sq1, sq2], self.turn)
                print("Move applied.")
                if self.board.get_queening() != None:
                    self.gui_board.queen(self.board.queening)
                    self.board.set_queening(None)
                self.board.update_history()
                print("History updated.")
                # check stopping conditions
                if self.board.check_threefold():
                    self.stop = True
                elif self.board.check_mate(self.turn):
                    self.stop = True
                else:  # proceed with game
                    # if self.turn:  # black
                    #     self.gui_board.black_timer.stop()
                    #     self.gui_board.white_timer.start()
                    # else:
                    #     self.gui_board.white_timer.stop()
                    #     self.gui_board.black_timer.start()
                    self.turn = not self.turn
                    self.board.unenpassant(self.turn)
                    self.gui_board.white_timer.toggle()
                    self.gui_board.black_timer.toggle()
                    print("It is now {}'s turn.".format(colors[self.turn]))
                    print("-----------------------------------------------------------------")
        else:
            print("*** Invalid move, try again. ***")
        if self.stop:
            return [420], [69]
        return self.board.w_coords, self.board.b_coords  # to update ChessBoard
    
    def endgame(self):
        if self.gui_board.white_timer.time_remaining <= 0:
            print("White ran out of time! Black wins. Game over.")
        elif self.gui_board.black_timer.time_remaining <= 0:
            print("Black ran out of time! White wins. Game over.")
        print("Destroying window...")
        self.root.destroy()  # same root as in gui class