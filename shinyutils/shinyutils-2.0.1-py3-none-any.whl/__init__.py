__version__ = "2.0.1"

import argparse

from shinyutils.matwrap import MatWrap
from shinyutils.subcls import (
    get_subclasses,
    get_subclass_names,
    get_subclass_from_name,
    build_subclass_object,
)
from shinyutils.argp import (
    ClassType,
    comma_separated_ints,
    KeyValuePairsType,
    LazyHelpFormatter,
    OutputFileType,
    OutputDirectoryType,
)
from shinyutils.logng import build_log_argp, conf_logging

shiny_arg_parser = argparse.ArgumentParser(formatter_class=LazyHelpFormatter)
build_log_argp(shiny_arg_parser)
conf_logging()
MatWrap.configure()
