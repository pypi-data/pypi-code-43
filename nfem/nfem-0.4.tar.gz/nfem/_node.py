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

    @location.setter
    def location(self, value):
        x, y, z = np.asarray(value, float)
        self.x.value = x
        self.y.value = y
        self.z.value = z

    @property
    def initial_location(self):
        return np.array([self.x.initial_value,
                         self.y.initial_value,
                         self.z.initial_value], float)

    @initial_location.setter
    def initial_location(self, value):
        x, y, z = np.asarray(value, float)
        self.x.initial_value = x
        self.y.initial_value = y
        self.z.initial_value = z

    @property
    def displacement(self):
        return self.location - self.initial_location

    @displacement.setter
    def displacement(self, value):
        self.location = self.initial_location + np.asarray(value, float)

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

    def dof(self, dof_type):
        if dof_type == 'x':
            return self.x
        if dof_type == 'y':
            return self.y
        if dof_type == 'z':
            return self.z
        raise RuntimeError()

    def draw(self, canvas):
        canvas.dot(self.location, text=f'Node {self.key}')
        if not self.z.is_active:
            canvas.support(self.location)
        external_force = self.external_force
        if np.linalg.norm(external_force) != 0.0:
            external_force /= np.linalg.norm(external_force)
            canvas.arrow_to(self.location, external_force, color='red', width=2)
