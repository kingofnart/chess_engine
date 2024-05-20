import copy
from tkinter import *
from grid import Grid
from gui import ChessBoard

class Game():

    def __init__(self):

        self.board = Grid()
        self.root = Tk()
        self.gui_board = ChessBoard(self.root, self.make_move, self.reset_game, self.board.w_coords, self.board.b_coords)
        self.turn = 0  # 0 = white, 1 = black
        self.board_history = []
        self.stop = False
        self.stop_condition = -1
        # stop conditions: 0=white flag, 1=black flag, 2=white checkmate; 
        # 3=white stalemate, 4=black checkmate, 5=black stalemate, 6=threefold

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
                    self.stop_condition = 6
                else:
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
                    else:  # proceed with game
                        self.turn = not self.turn
                        self.board.unenpassant(self.turn)
                        self.gui_board.white_timer.toggle()
                        self.gui_board.black_timer.toggle()
                        print("It is now {}'s turn.".format(colors[self.turn]))
                        print("-----------------------------------------------------------------")
        else:
            print("*** Invalid move, try again. ***")
        if self.stop:
            self.gui_board.white_timer.stop()
            self.gui_board.black_timer.stop()
            self.endgame()
        return self.board.w_coords, self.board.b_coords  # to update ChessBoard
    
    def endgame(self):
        if self.gui_board.white_timer.time_remaining <= 0:
            print("White ran out of time! Black wins. Game over.")
            self.stop_condition = 0
        elif self.gui_board.black_timer.time_remaining <= 0:
            print("Black ran out of time! White wins. Game over.")
            self.stop_condition = 1
        match self.stop_condition:
            case 0: text = "White ran out of time!\nBlack wins.\nGame over."
            case 1: text = "Black ran out of time!\nWhite wins.\nGame over."
            case 2: text = "White checkmated Black.\nWhite wins.\nGame over."
            case 3: text = "White stalemated Black.\nIt's a draw.\nGame over."
            case 4: text = "Black checkmated White.\nBlack wins.\nGame over."
            case 5: text = "Black stalemated White.\nIt's a draw.\nGame over."
            case 6: text = "Threefold repetition reached.\nIt's a draw.\nGame over."
        self.gui_board.ending_popup(text)

    def reset_game(self, win):
        self.board.reset()
        self.gui_board.wc = self.board.w_coords
        self.gui_board.wc = self.board.w_coords
        self.gui_board.white_timer.reset()
        self.gui_board.black_timer.reset()
        self.gui_board.update()
        win.destroy()
        self.stop = False
        self.turn = 0
        self.stop_condition = -1
        self.play()