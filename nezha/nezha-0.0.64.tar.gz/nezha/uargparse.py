import argparse

class NotErrorArgumentParser(argparse.ArgumentParser):
    """
    if arg is not defined, the class will be silent.
    """

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        return args
