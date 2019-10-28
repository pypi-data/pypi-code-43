from ._dof import Dof
import numpy as np


class Node:
    def __init__(self, key, x, y, z):
        self.key = key
        self.x = Dof(x)
        self.y = Dof(y)
        self.z = Dof(z)

    @property
    def location(self):
        return np.array([self.x, self.y, self.z], float)

    def draw(self, canvas):
        canvas.dot(self.location, text=f'Node {self.key}')
        if not self.z.is_active:
            canvas.support(self.location)
