class Truss:
    def __init__(self, key, node_a, node_b):
        self.key = key
        self.node_a = node_a
        self.node_b = node_b

    def draw(self, canvas):
        location_a = self.node_a.location
        location_b = self.node_b.location

        canvas.line(location_a, location_b, text=f'Truss {self.key}')
