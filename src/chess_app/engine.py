import random
import copy

class Engine():

    def __init__(self, board):
        self.board = board


    def random_move(self, color):
        self.board.attacked_squares(color, 1)
        e_valid_moves = self.board.get_valid_moves(color)
        move_idx = random.randint(0, len(e_valid_moves) - 1)
        return e_valid_moves[move_idx]
    

    # returns the material difference between white and black
    def evaluate(self, input_board):
        input_board.update_material_count()
        return input_board.get_material_diff()


    # method to recursively find the optimal move for each color up to depth
    # -> optimal move for white is mazimizing the score
    # -> optimal move for black is minimizing the score
    # used for evaluating all moves at all levels (0->depth) ** does not save the move **
    def minimax_recursive(self, color, depth, input_board, alpha, beta):
        # print(f"depth: {depth}, color: {color}")
        # stop condition
        # color about to move, check game_ended with not color
        if depth == 0 or self.game_ended(int(not color), input_board):
            return self.evaluate(input_board)
        # save current coordinates to undo move
        prev_coords_w = input_board.w_coords.copy()
        prev_coords_b = input_board.b_coords.copy()

        # recursive case
        if color:
            # color=black, minimize the score
            best_score = float('inf')
            # find lowest score given optimal play from white
            for move in input_board.get_valid_moves(color):
                input_board.apply_move(move, color)
                score = self.minimax_recursive(int(not color), depth - 1, input_board, alpha, beta)
                input_board.undo_move(prev_coords_w, prev_coords_b)
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            # color=white, maximize the score
            best_score = float('-inf')
            # find highest score given optimal play from black
            for move in input_board.get_valid_moves(color):
                input_board.apply_move(move, color)
                score = self.minimax_recursive(int(not color), depth - 1, input_board, alpha, beta)
                input_board.undo_move(prev_coords_w, prev_coords_b)
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score


    # method to call minimax_recursive for each move at current position and save the move
    def minimax(self, color, depth):
        # finding best move for current position
        best_move = None
        best_score = float('inf') if color else float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        tmp_board = copy.deepcopy(self.board)
        # save coords for undo move
        prev_coords_w = tmp_board.w_coords.copy()
        prev_coords_b = tmp_board.b_coords.copy()
        # find best move and return associated move
        for move in tmp_board.get_valid_moves(color):
            tmp_board.apply_move(move, color)
            score = self.minimax_recursive(int(not color), depth - 1, tmp_board, alpha, beta)
            tmp_board.undo_move(prev_coords_w, prev_coords_b)
            if (color and score < best_score) or (not color and score > best_score):
                best_score = score
                best_move = move
            if color: # black - minimize
                beta = min(beta, best_score)
            else: # white - maximize
                alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        del tmp_board
        return best_move


    # check if game has ended (by checkmate, stalemate or threefold repetition)
    def game_ended(self, color2check, input_board):
        if input_board.check_mate(color2check) != (-1, -1) or input_board.check_threefold():
            return True
        else:
            return False