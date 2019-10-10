import math

from rox.core.entities.flag import Flag

class InternalFlags:
    def __init__(self, experiment_repository, parser):
        self.experiment_repository = experiment_repository
        self.parser = parser

    def is_enabled(self, flag_name):
        internal_experiment = self.experiment_repository.get_experiment_by_flag(flag_name)
        if internal_experiment is None:
            return False

        value = self.parser.evaluate_expression(internal_experiment.condition, None).string_value()
        return value == Flag.FLAG_TRUE_VALUE

    def get_number_value(self, flag_name):
        internal_experiment = self.experiment_repository.get_experiment_by_flag(flag_name)
        if internal_experiment is None:
            return None

        value = self.parser.evaluate_expression(internal_experiment.condition, None).string_value()
        try: 
            number = float(value)
            if math.isnan(number):
                return None
            return number
        except ValueError:
            return None
