from tkinter import *
import tkinter as tk
from tkinter import ttk
from functools import partial

class ChessBoard:

    def __init__(self, root, make_move, white_coords, black_coords):
        
        self.root = root
        self.callback = make_move
        self.wc = white_coords
        self.bc = black_coords
# piece id key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
#             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
        self.names = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                      8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
        root.title("Chess")
        self.first_click = None
        self.mainframe = ttk.Frame(self.root)
        self.mainframe.grid(column=0, row=0)
        self.create_board()

    def create_board(self):
        for nrow in range(8):
            for ncol in range(8):
                for i in range(16):
                    if 7-nrow == self.wc[i][0] and ncol == self.wc[i][1]:
                        txt = self.names[i] + 'w'
                        break
                    elif 7-nrow == self.bc[i][0] and ncol == self.bc[i][1]:
                        txt = self.names[i] + 'b'
                        break
                    else:
                        txt = "__"
                btn = tk.Button(self.mainframe, text = txt)
                btn.grid(row=nrow, column=ncol)
                btn.config(command=partial(self.handle_click, ncol, 7-nrow, btn))

    def handle_click(self, col, row, button):
        pos = (row, col)
        if self.first_click is None: # need to get two clicks
            self.first_click = pos
            button.config(relief=SUNKEN) # let them know it's clicked
        elif self.first_click != pos: # can't move to same square
            self.wc, self.bc = self.callback(self.first_click, pos) # send (move0, move1) to play class
            self.update()

    def update(self):
        # resetting sunken button and first click
        self.first_click = None
        for child in self.mainframe.winfo_children():
            if isinstance(child, tk.Button): # safety
                child.config(relief=RAISED)
                row = child.grid_info()['row']
                col = child.grid_info()['column']
                # updating piece locations
                for i in range(16):
                    if 7-row == self.wc[i][0] and col == self.wc[i][1]:
                        child.config(text = self.names[i] + 'w')
                        break
                    elif 7-row == self.bc[i][0] and col == self.bc[i][1]:
                        child.config(text = self.names[i] + 'b')
                        break
                    else:
                        child.config(text = '__')
