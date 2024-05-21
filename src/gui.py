from timer import Timer
import tkinter as tk
from tkinter import *
from functools import partial

class ChessBoard:


    def __init__(self, root, make_move, end_da_game, white_coords, black_coords):
        
        self.root = root
        self.callback = make_move
        self.end_callback = end_da_game
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
        self.mainframe = Frame(self.root, bg="#b3b1b1")
        self.mainframe.grid(column=0, row=0)
        self.white_timer = Timer(self.mainframe, "#ededed", "#1a1a1a")
        self.black_timer = Timer(self.mainframe, "#404040", "#f5f5f5")
        self.color2name = {0: "White", 1: "Black"}
        self.num2colors = {0: ["#ffffff", "#000000"], 1: ["#000000", "#ffffff"]}
        self.turn_label = Label(self.mainframe, text="{} to move".format(self.color2name[0]),
                                   width=15, height=2, bg=self.num2colors[0][0], 
                                   fg=self.num2colors[0][1], font=("Arial", "16"))
        self.load_images()  # first load images
        self.create_board()  # then create board
        self.starting_popup()  # then run starting popup
        # then wait for user input and eventually game end


    # function to preload in all the piece images
    def load_images(self):
        # make image dictionary to store piece images
        self.images = {}
        for name in ['K', 'Q', 'R', 'N', 'B', 'P']:
            self.images[name + 'w'] = PhotoImage(file=f'resources/{name}w.png')
            self.images[name + 'b'] = PhotoImage(file=f'resources/{name}b.png')
        # also add empty image to images dictionary
        self.images['_'] = tk.PhotoImage(width=135, height=135)
    

    # function that creates all the button widgets and puts them in the correct spot
    # with the correct command function
    def create_board(self):
        # want to give extra space for the timers
        self.root.grid_rowconfigure(0, weight = 1)
        self.root.grid_rowconfigure(9, weight = 1)
        color1 = "#F5D7A4"  # light squares
        color2 = "#694507"  # dark squares
        # maybe allow different color schemes?
        self.turn_label.grid(row=0, column=0, columnspan=3, sticky='E')
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
                btn = Button(self.mainframe, image=img, bg=color, activebackground="#90941f", width=btn_size, height=btn_size)
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


    # function to show popup of how game ended
    def ending_popup(self, txt):
        popup = Toplevel(self.mainframe, bg="#354d52")
        popup.title("Game Outcome")
        label = Label(popup, text=txt, font=("OCR A EXTENDED", 16), bg="#d42202")
        label.grid(row=0, column=0)
        popup.config(width=label.winfo_width())
        Button(popup, text="New Game", font=('ALGERIAN 15'), command=partial(self.tmp_fn_idk_why, popup), 
                  bg="#759956", width=10, height=2, activebackground="#078c0e").grid(row=1, column=0, pady=20)
        self.center_popup(popup)


    # need this for new game button to show up
    def tmp_fn_idk_why(self, popup):
        self.end_callback(popup)


    # function to update timers and turn indicator after move has been applied
    def update_turn(self, turn):
        self.white_timer.toggle()
        self.black_timer.toggle()
        self.turn_label.config(text="{} to move".format(self.color2name[turn]), 
                               bg=self.num2colors[turn][0], fg=self.num2colors[turn][1])


    # function to give countdown for game start
    def starting_popup(self):
        # need these to be attributes to be used in countdown()
        self.start_popup = Toplevel(self.mainframe, bg="#88b9ba")
        # keep starting popup over main window
        self.start_popup.transient(self.root)
        self.start_popup.lift(self.root)
        self.start_popup.grab_set()  # don't let user play yet
        self.start_popup.geometry("500x250")
        self.count = 5  
        self.label = tk.Label(self.start_popup, text="Game starting in {}...".format(self.count), 
                         font=("OCR A EXTENDED", 25), bg="#ff3c00", fg="#000000", height=3)
        self.label.pack(expand=True)
        self.center_popup(self.start_popup)
        self.countdown()


    # function to recursively count down + wait second then destroy
    def countdown(self):
        if self.count > 0:
            self.label.config(text="Game starting in {}...".format(self.count))
            self.count -= 1
            self.root.after(1000, self.countdown)
        else:
            self.label.config(text="Commence battle!", font=("Eras Demi ITC", 30), bg="#12d400", fg="#ffffff", height=2)
            self.root.after(1000, self.destroy_popup)


    # function to make sure popup is destroyed first then whites clock starts and the board isnt minimized
    def destroy_popup(self):
        self.start_popup.destroy()
        self.white_timer.toggle()  # Start white's clock
        self.root.deiconify()  # Ensure main window is not minimized


    # function to center starting popup over chessboard
    def center_popup(self, popup):
        self.root.update()  # do not use update_idletasks here
        main_width = self.root.winfo_width()
        main_height = self.root.winfo_height()
        main_x = self.root.winfo_x()
        main_y = self.root.winfo_y()
        popup.update_idletasks()  # Ensure all sizes are updated
        popup_width = popup.winfo_width()
        popup_height = popup.winfo_height()
        popup_x = main_x + (main_width // 2) - (popup_width // 2)
        popup_y = main_y + (main_height // 2) - (popup_height // 2)
        popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")
