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

    @property
    def external_force(self):
        return np.array([self.x.external_force,
                         self.y.external_force,
                         self.z.external_force], float)

    @external_force.setter
    def external_force(self, value):
        fx, fy, fz = np.asarray(value, float)
        self.x.external_force = fx
        self.y.external_force = fy
        self.z.external_force = fz

    def draw(self, canvas):
        canvas.dot(self.location, text=f'Node {self.key}')
        if not self.z.is_active:
            canvas.support(self.location)
        external_force = self.external_force
        if np.linalg.norm(external_force) != 0.0:
            external_force /= np.linalg.norm(external_force)
            canvas.arrow_to(self.location, external_force, color='red', width=2)
