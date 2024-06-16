import random

class Engine():

    def __init__(self, board):
        self.board = board

    def random_move(self, color):
        self.board.attacked_squares(color, 1)
        e_valid_moves = self.board.get_valid_moves(color)
        move_idx = random.randint(0, len(e_valid_moves) - 1)
        return e_valid_moves[move_idx]