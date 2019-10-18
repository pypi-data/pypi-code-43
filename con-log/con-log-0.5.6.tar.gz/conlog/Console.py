from .expr_debug import _expr_debug, _cdebug

from colored import fore, back, style

from conlog.formats import format_dict, format_caller


class Console:
    def __init__(self, module, logger):
        self.logger = logger
        self.module = module
        # _cdebug("Console", logger, module)

    def log(self, rstr):
        print(rstr)

    def debug(self, rstr):
        """ Log the raw string as f' string with evaluated expressions.
            Keyword arguments:
        """
        expr_msg, fn_name = _expr_debug(rstr)
        name = format_caller(self.module, fn_name)
        format = f"{name} {expr_msg}"
        self.logger.debug(format)

    def dir(self, xdict):
        self.logger.debug(format_dict(xdict))
