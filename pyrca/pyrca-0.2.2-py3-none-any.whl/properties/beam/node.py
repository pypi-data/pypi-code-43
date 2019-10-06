class Node:
    # Represents a node in a section

    x = None
    y = None

    def __init__(self, lx, ly):
        self.x = lx
        self.y = ly

    def __repr__(self):
        return f'({self.x}, {self.y})'
