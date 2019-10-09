import os
import warnings

from simple_settings import LazySettings


class FailsafeModuleStrategy:
    name = 'python_failsafe'

    @staticmethod
    def is_valid_file(file_name):
        return True

    @staticmethod
    def load_settings_file(settings_file):
        if not os.path.exists(settings_file):
            warnings.warn(f'Settings file {settings_file} does not exist.')
        return dict()


def create_settings(*specs):
    settings = LazySettings(*specs)
    settings.add_strategy(FailsafeModuleStrategy)
    settings.setup()
    return settings
