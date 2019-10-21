from zml.exceptions import VariableNotDefinedException
from zml.semantic import *


class RenderingContext(object):

    def get_var(self, variable_descriptor):
        if variable_descriptor in self.local_context:
            return self.local_context[variable_descriptor]
        if variable_descriptor in self.global_context:
            return self.global_context[variable_descriptor]
        raise VariableNotDefinedException

    def set_var(self, variable_descriptor, value):
        self.local_context[variable_descriptor] = value

