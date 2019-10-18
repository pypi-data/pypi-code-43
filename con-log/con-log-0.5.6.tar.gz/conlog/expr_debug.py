import re
import inspect

from colored import fore, back, style
from conlog.formats import format_dict, format_caller, format_idn

regex_pat = re.compile(r"\s*\((.+?)\)$")
regex_fstr = re.compile(r"\s*\"(.+?)\"$")
regex_expr = re.compile(r"(\{.*?\=\})")


# Uses ugly hack to support f"{expr=}" in 3.7+\
def _expr_debug(fstr, patt="console.debug"):
    py_version = 37

    if py_version < 38:

        try:
            # Get 2 stack frames back
            context = inspect.stack()[2]
            frame = context.frame
            call_lines = "".join([line.strip() for line in context.code_context])
            # print(f"{fore.GREEN}{style.BOLD}_expr_debug::{style.RESET} ",call_lines)

            fmatch = re.search(regex_pat, call_lines)
            match = fmatch if fmatch else re.search(regex_fstr, call_lines)

            if match:
                a = regex_expr.findall(fstr)

                ae = [re.sub(r"\{|\}|\=", "", e) for e in a]

                expstr = [
                    f"{format_idn(e)}=" + str(eval(e, frame.f_globals, frame.f_locals))
                    for e in ae
                ]
                repl = dict(zip(a, expstr))
                out_str = re.sub(
                    regex_expr, lambda mx: repl.get(mx.group(), mx.group()), fstr
                )
                return (out_str, context.function)
            else:
                return (fstr, context.function)
        finally:
            del context
            del frame


### Internal function to debug Conlog itself
def _cdebug(fstr, *args):
    enabled = False
    if enabled:
        expstr = __ = _expr_debug(fstr, patt="_cdebug")
        print(expstr)
