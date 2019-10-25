class ChoiceHelper(object):
    def __init__(self, choice_tuple):
        self.choices = choice_tuple
        self.choice_literals_dict = {k: v for v, k in self.choices}
        self.choice_values_dict = {v: k for v, k in self.choices}

    def get_value(self, literal):
        return self.choice_literals_dict.get(literal)

    def get_literal(self, value):
        return self.choice_values_dict.get(value)
