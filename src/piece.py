class Piece:
    def __init__(self, color, type, id):
        self.color = color
        self.type = type
        self.id = id
        self.captured = False
        self.moved = False
        self.enpassant = False
    
    def set_captured(self, val):
        self.captured = val

    def set_moved(self, val):
        self.moved = val

    def set_enpassant(self, val):
        self.enpassant = val

    def get_moved(self):
        return self.moved
    
    def get_enpassant(self):
        return self.enpassant
    
    def get_captured(self):
        return self.captured
    
# 0 = King; 1 = Queen; 2 = Rook; 3 = Knight; 4 = Bishop; 5 = Pawn
