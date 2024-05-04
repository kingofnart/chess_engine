from piece import Piece

# 0 = King, 1 = Queen, 2 = Rook, 3 = Bishop, 4 = Knight, 5 = Pawn
names = {0: "King", 1: "Queen", 2: "Rook", 3: "Bishop", 4: "Knight", 5: "Pawn"}
row1 = [Piece(0,2), Piece(0,4), Piece(0,3), Piece(0,1), Piece(0,0), Piece(0,3), Piece(0,4), Piece(0,2)]
row2 = [Piece(0,5) for _ in range(8)]
row3 = [0 for i in range(8)]
row4, row5, row6 = row3, row3, row3
row7 = [Piece(1,5) for _ in range(8)]
row8 = [Piece(1,2), Piece(1,4), Piece(1,3), Piece(1,1), Piece(1,0), Piece(1,3), Piece(1,4), Piece(1,2)]

board = [row1, row2, row3, row4, row5, row6, row7, row8]
