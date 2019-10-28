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
