"""named resource"""
from simpy import Resource


class NamedResource(Resource):
    """simpy resource with name"""

    def __init__(self, env, name, capacity=1):
        super().__init__(env, capacity=capacity)

        self.name = name
