class Piece:
    def __init__(self, color, id):
        self.color = color
        self.id = id
        self.captured = 0
        self.moved = 0
        self.enpassant = 0
    
    def set_captured(self, val):
        self.captured = val

    def set_moved(self, val):
        self.moved = val

    def set_enpassant(self, val):
        self.enpassant = val
# 0 = King, 1 = Queen, 2 = Rook, 3 = Knight, 4 = Bishop, 5 = Pawn