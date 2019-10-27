import inspect
import argparse


class cli(object):
    def __init__(self, desc=""):
        self.description = desc
        self.functions = dict()

    def setDescription(self, desc):
        self.description = desc

    # decorator for runnable functions
    def command(self, f):
        fName = f.__name__
        if fName in self.functions:
            print("Function {} already registered, overwriting it..")

        self.functions[fName] = f
        return f

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if len(self.functions) > 0:
            self.parse_args()

    def parse_args(self):
        parser = argparse.ArgumentParser(description=self.description)
        subparsers = parser.add_subparsers(help="Select one of the following subcommands:", dest='command', metavar="subcommand")
        subparsers.required = True

        for fName, f in self.functions.items():
            sub_parser = subparsers.add_parser(fName, help=f.__doc__, description=f.__doc__)
            for param in inspect.signature(f).parameters.values():
                tpe = param.annotation
                if tpe is inspect.Parameter.empty:
                    tpe = str
                if param.default is not inspect.Parameter.empty:
                    prefix = "-" if len(param.name) == 1 else "--"
                    sub_parser.add_argument(prefix + param.name,
                                            help="type: {}, default={}".format(tpe.__name__, param.default),
                                            type=tpe, default=param.default)
                else:
                    sub_parser.add_argument(param.name, help="type: " + tpe.__name__,
                                            type=tpe)

        cmd_args = parser.parse_args()
        fName = cmd_args.command
        f = self.functions[fName]
        args = cmd_args._get_args()
        kwargs = {n: v for n, v in cmd_args._get_kwargs() if n != "command"}
        f(*args, **kwargs)
