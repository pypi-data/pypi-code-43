"""argp.py: utilities for argparse."""

from argparse import ArgumentTypeError, MetavarTypeHelpFormatter, FileType, SUPPRESS
import logging
import os
from pathlib import Path
from unittest.mock import patch

import crayons

from shinyutils.subcls import get_subclass_from_name, get_subclass_names


class LazyHelpFormatter(MetavarTypeHelpFormatter):

    # pylint: disable=no-member
    CHOICE_SEP = "/"
    DEF_CSTR = str(crayons.green("default"))
    REQ_CSTR = str(crayons.green("required"))
    OPT_CSTR = str(crayons.green("optional"))
    COLOR_CHOICE = lambda s: str(crayons.blue(s, bold=False))
    COLOR_DEFAULT = lambda s: str(crayons.blue(s, bold=True))
    COLOR_METAVAR = lambda s: str(crayons.red(s, bold=True))

    def _format_action(self, action):
        if not action.help and action.option_strings:
            # dummy help for optional arguments for proper formatting
            action.help = " "

        if action.nargs == 0:
            # hack to fix length of option strings
            # when nargs=0, there's no metavar, or the extra color codes
            action.option_strings[0] += str(crayons.normal("", bold=True))

        return super()._format_action(action)

    def _format_action_invocation(self, action):
        if action.option_strings and action.nargs != 0:
            # show action as -s/--long ARGS rather than -s ARGS, --long ARGS
            combined_opt_strings = "/".join(action.option_strings)
            with patch.object(action, "option_strings", [combined_opt_strings]):
                return super()._format_action_invocation(action)

        with patch.object(  # format positional arguments same as optional
            action, "option_strings", action.option_strings or [action.dest]
        ):
            return super()._format_action_invocation(action)

    def _get_help_string(self, action):
        if action.choices:
            choice_strs = list(map(LazyHelpFormatter.COLOR_CHOICE, action.choices))
            try:
                def_pos_in_choices = action.choices.index(action.default)
            except ValueError:
                pass
            else:
                # mark the default option with '[]'
                if def_pos_in_choices != -1:
                    defstr = LazyHelpFormatter.COLOR_DEFAULT(action.default)
                    choice_strs[def_pos_in_choices] = f"[{defstr}]"

            _h = self.CHOICE_SEP.join(choice_strs)
            if action.required and action.option_strings:
                # indicate optional arguments which are required
                _h = f"{self.REQ_CSTR} {_h}"
        elif action.required:
            if action.option_strings:
                _h = self.REQ_CSTR
            else:
                # positional arguments are always required - no need to specify
                return super()._get_help_string(action)
        elif action.default is None:
            # optional argument
            _h = self.OPT_CSTR
        elif action.default != SUPPRESS:
            _h = f"{self.DEF_CSTR}: {LazyHelpFormatter.COLOR_DEFAULT(action.default)}"
        else:
            return super()._get_help_string(action)
        return action.help + f" ({_h})"

    def _metavar_formatter(self, action, default_metavar):
        with patch.object(action, "choices", None):
            # don't put choices in the metavar
            base_formatter = super()._metavar_formatter(action, default_metavar)

        def color_wrapper(tuple_size):
            f = base_formatter(tuple_size)
            if not f:
                return f
            return (
                LazyHelpFormatter.COLOR_METAVAR(" ".join(map(str, f))),
                *(("",) * (len(f) - 1)),  # collapse to single metavar
            )

        return color_wrapper

    def __init__(self, *args, **kwargs):
        kwargs["max_help_position"] = float("inf")
        kwargs["width"] = float("inf")
        super().__init__(*args, **kwargs)

    def add_usage(self, *args, **kwargs):
        pass

    def start_section(self, heading):
        if heading == "positional arguments":
            heading = "arguments"
        elif heading == "optional arguments":
            heading = "options"
        super().start_section(heading)


def comma_separated_ints(string):
    try:
        return list(map(int, string.split(",")))
    except:
        raise ArgumentTypeError(f"`{string}` is not a comma separated list of ints")


class InputFileType(FileType):
    def __init__(self, mode="r", **kwargs):
        if mode not in {"r", "rb"}:
            raise ValueError("mode should be 'r'/'rb'")
        super().__init__(mode, **kwargs)


class OutputFileType(FileType):
    def __init__(self, mode="w", **kwargs):
        if mode not in {"w", "wb"}:
            raise ValueError("mode should be 'w'/'wb'")
        super().__init__(mode, **kwargs)

    def __call__(self, string):
        file_dir = os.path.dirname(string)
        if file_dir and not os.path.exists(file_dir):
            logging.warning(f"no directory for {string}: trying to create")
            try:
                os.makedirs(file_dir)
            except Exception as e:
                raise ArgumentTypeError(f"could not create {file_dir}: {e}")
            logging.info(f"created {file_dir}")
        return super().__call__(string)


class InputDirectoryType:
    def __call__(self, string):
        if not os.path.exists(string):
            raise ArgumentTypeError(f"no such directory: {string}")
        return Path(string)


class OutputDirectoryType:
    def __call__(self, string):
        if not os.path.exists(string):
            logging.warning(f"{string} not found: trying to create")
            try:
                os.makedirs(string)
            except Exception as e:
                raise ArgumentTypeError(f"cound not create {string}: {e}")
            logging.info(f"created {string}")
        return Path(string)


class ClassType:
    def __init__(self, cls):
        self.cls = cls

    def __call__(self, string):
        try:
            return get_subclass_from_name(self.cls, string)
        except RuntimeError:
            choices = [f"'{c}'" for c in get_subclass_names(self.cls)]
            raise ArgumentTypeError(
                f"invalid choice: '{string}' " f"(choose from {', '.join(choices)})"
            )


class KeyValuePairsType:
    def __call__(self, string):
        out = dict()
        try:
            for kv in string.split(","):
                k, v = kv.split("=")
                try:
                    v = int(v)
                except ValueError:
                    try:
                        v = float(v)
                    except ValueError:
                        pass
                out[k] = v
        except Exception as e:
            raise ArgumentTypeError(e)
        return out
