from timer import Timer
import tkinter as tk
from functools import partial

class ChessBoard:

    def __init__(self, root, make_move, end_da_game, white_coords, black_coords):
        
        self.root = root
        self.callback = make_move
        self.wc = white_coords
        self.bc = black_coords
# piece id key: [king (0), queen (1), a rook (2), h rook (3), b knight (4), 
#             g knight (5), c bishop (6), f bishop (7), pawns a-h (8-15)]
        self.names_w = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                      8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
        self.names_b = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                      8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
        root.title("Chess")
        self.first_click = None
        self.mainframe = tk.Frame(self.root)
        self.mainframe.grid(column=0, row=0)
        self.white_timer = Timer(self.mainframe, end_da_game, "#dbdbdb", "#1a1a1a")
        self.black_timer = Timer(self.mainframe, end_da_game, "#404040", "#f5f5f5")
        self.load_images()  # first load images
        self.create_board()  # then create board

    # function to preload in all the piece images
    def load_images(self):
        # make image dictionary to store piece images
        self.images = {}
        for name in ['K', 'Q', 'R', 'N', 'B', 'P']:
            self.images[name + 'w'] = tk.PhotoImage(file=f'resources/{name}w.png')
            self.images[name + 'b'] = tk.PhotoImage(file=f'resources/{name}b.png')
        # also add empty image to images dictionary
        self.images['_'] = tk.PhotoImage(width=135, height=135)
    
    # function that creates all the button widgets and puts them in the correct spot
    # with the correct command function
    def create_board(self):
        # want to give extra space for the timers
        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_rowconfigure(9, weight = 1)
        color1 = "#F5D7A4"  # light brown/tan
        color2 = "#694507"  # dark brown
        # maybe allow different color schemes?
        self.black_timer.timer_label.grid(row=0, column=5, columnspan=3, sticky='E')
        for nrow in range(8):
            for ncol in range(8):
                # colors for checkerboard pattern
                color = color1 if (nrow + ncol) % 2 == 0 else color2
                img = self.images['_']
                for i in range(16):
                    if 7-nrow == self.wc[i][0] and ncol == self.wc[i][1]:
                        img = self.images[self.names_w[i] + 'w']
                        break
                    elif 7-nrow == self.bc[i][0] and ncol == self.bc[i][1]:
                        img = self.images[self.names_b[i] + 'b']
                        break
                btn_size = 75
                btn = tk.Button(self.mainframe, image=img, bg=color, width=btn_size, height=btn_size)
                btn.grid(row=nrow+1, column=ncol)
                btn.config(command=partial(self.handle_click, ncol, 7-nrow, btn))
                btn.image = img  # make reference, avoid garbage collection
        self.white_timer.timer_label.grid(row=9, column=5, columnspan=3, sticky='E')

    # function to get user input
    # user input must be two clicks of different locations
    # call function from Game class when input is received
    def handle_click(self, col, row, button):
        pos = (row, col)
        if self.first_click is None:  # need to get two clicks
            self.first_click = pos
            button.config(relief=tk.SUNKEN)  # let them know it's clicked
        elif self.first_click != pos:  # can't move to same square
            # got both clicks, now call input function (make_move) with clicks as input
            # save new coordinates & update gui to display the move
            self.wc, self.bc = self.callback(self.first_click, pos)  # send (move0, move1) to play class
            # worst case this has to be two kings and still that is a draw
            if len(self.wc) == 1 and len(self.bc) == 1:
                print("Destroying window...")
                self.root.destroy()
            else:
                self.update()

    # function to update images on buttons for piece locations
    def update(self):
        # resetting sunken button and first click
        self.first_click = None
        for child in self.mainframe.winfo_children():
            if isinstance(child, tk.Button):  # safety
                child.config(relief=tk.RAISED)
                row = child.grid_info()['row']
                col = child.grid_info()['column']
                # updating piece locations
                for i in range(16):
                    if 8-row == self.wc[i][0] and col == self.wc[i][1]:
                        child.config(image=self.images[self.names_w[i] + 'w'])
                        break
                    elif 8-row == self.bc[i][0] and col == self.bc[i][1]:
                        child.config(image=self.images[self.names_b[i] + 'b'])
                        break
                    else:
                        child.config(image=self.images['_'])

    # function to change name of queened pawn
    def queen(self, piece):
        if piece.get_color():  # black 
            self.names_b[piece.id] = 'Q'
        else:  # white
            self.names_w[piece.id] = 'Q'