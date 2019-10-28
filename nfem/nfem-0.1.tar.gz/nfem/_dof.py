class Dof:
    def __init__(self, value, is_active=True):
        self.initial_value = float(value)
        self.value = float(value)
        self.is_active = is_active
        self.external_force = 0.0

    def __float__(self):
        return self.value
