from piece import Piece

class Grid():
    def __init__(self):
        row1 = [Piece(0,2), Piece(0,4), Piece(0,3), Piece(0,1), Piece(0,0), Piece(0,3), Piece(0,4), Piece(0,2)]
        row2 = [Piece(0,5) for _ in range(8)]
        row3 = [0 for _ in range(8)]
        row4, row5, row6 = row3, row3, row3
        row7 = [Piece(1,5) for _ in range(8)]
        row8 = [Piece(1,2), Piece(1,4), Piece(1,3), Piece(1,1), Piece(1,0), Piece(1,3), Piece(1,4), Piece(1,2)]
        self.grid = [row1, row2, row3, row4, row5, row6, row7, row8]

    # 0 = King, 1 = Queen, 2 = Rook, 3 = Bishop, 4 = Knight, 5 = Pawn
    def valid_move(self, move):
        piece = self.grid[move[0][0]][move[0][1]]
        
        if (piece != 0):
            match piece.id:
                #case 0:

                #case 1:

                #case 2:

                #case 3:

                #case 4:

                case 5:
                    if piece.color == 0:
                        if move[0][0] == move[1][0] - 1:
                            return 1
                        else: return 0
                    elif piece.color == 1:
                        if move[0][0] == move[1][0] + 1:
                            return 1
                        else: return 0
                case _:
                    print("Piece id error")
                    return -1
        else:
            print("not piece")
            return -1