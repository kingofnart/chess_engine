class Piece:
    def __init__(self, color, id):
        self.color = color
        self.id = id
        self.captured = 0
# 0 = King, 1 = Queen, 2 = Rook, 3 = Bishop, 4 = Knight, 5 = Pawn