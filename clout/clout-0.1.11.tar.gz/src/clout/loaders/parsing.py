import collections
import functools
import math
import shlex
import subprocess
import sys
import typing as t

import attr
import click
import lark

import clout.exceptions

from .. import util


ALWAYS_ACCEPT = True

HELP_COMMAND = "HELP_COMMAND"


class CountingBaseCommand:
    def __init__(self, *args, nargs=1, required=False, **kwargs):
        self.nargs = nargs
        self.required = required

        super().__init__(*args, **kwargs)

    @property
    def multiple(self):
        return self.nargs != 1


class CountingGroup(CountingBaseCommand, click.Group):
    pass


class CountingCommand(CountingBaseCommand, click.Command):
    pass


@functools.singledispatch
def to_lark(obj: object):
    raise NotImplementedError(obj)


def quote(s):
    return '"' + s + '"'


def par(s):
    return f"({s})"


def one_of(items):
    items = list(items)
    if len(items) == 1:
        return str(items[0])
    return par(" | ".join(items))


def name_rule(obj) -> str:
    return f"{obj.name.lstrip('-').replace('-', '_')}_{id(obj)}"


@to_lark.register
def _(option: click.Option):
    if option.is_flag:
        return (
            f"{name_rule(option)} : "
            + "|".join(quote(decl) for decl in option.opts)
            + "\n"
        )
    return (
        f"{name_rule(option)} : "
        + one_of(quote(decl) + ' "="? value' for decl in option.opts)
        + "\n"
    )


@to_lark.register
def _(arg: click.Argument):
    return f"{name_rule(arg)} : value\n"


def min_params(cmd: click.BaseCommand) -> int:
    return sum(
        1 if p.nargs == -1 or p.multiple else p.nargs
        for p in cmd.params
        if p.required or not p.default
    )


def max_params(cmd: click.BaseCommand) -> t.Union[int, float]:
    return sum(math.inf if p.nargs == -1 or p.multiple else p.nargs for p in cmd.params)


@to_lark.register
def _(cmd: CountingCommand):
    optionals = [name_rule(p) for p in cmd.params if not p.required or p.default]
    requireds = [name_rule(p) for p in cmd.params if p.required]
    params = one_of(optionals + requireds)

    if max_params(cmd) == math.inf:
        params += f"+"
    else:
        params += f" ~ {min_params(cmd)}..{max_params(cmd)}"
    out = f"{name_rule(cmd)} : {quote(cmd.name)} {params} \n"
    for p in cmd.params:
        out += to_lark(p)
    return out


@to_lark.register
def _(grp: CountingGroup):
    if not grp.commands:
        return to_lark.dispatch(CountingCommand)(grp)
    command = one_of(name_rule(c) for c in grp.commands.values())

    optionals = [name_rule(p) for p in grp.params if not p.required]
    requireds = [name_rule(p) for p in grp.params if p.required]
    params = one_of(optionals + requireds)

    if grp.params:
        out = f"{name_rule(grp)} : {quote(grp.name)} ({command}|{params})+ \n"
    else:
        out = f"{name_rule(grp)} : {quote(grp.name)} {command}+ \n"

    for c in grp.commands.values():
        out += to_lark(c)
    for p in grp.params:
        out += to_lark(p)
    return out


def build_grammar(grp):
    grammar = to_lark(grp)
    grammar += "?value : /\S+/\n"
    grammar += f"?start : {name_rule(grp)}\n"
    grammar += "%import common.CNAME\n"
    grammar += "%import common.WS -> _WHITE\n"
    grammar += "%ignore _WHITE\n"

    return grammar


def get_base_commands(grp: click.BaseCommand) -> t.Iterator[click.BaseCommand]:
    yield grp
    if not hasattr(grp, "commands"):
        return
    for cmd in grp.commands.values():
        yield from get_base_commands(cmd)


class Walker(lark.Visitor):
    def __init__(self, *args, group, **kwargs):
        self.group = group
        super().__init__(*args, **kwargs)
        base_commands = list(get_base_commands(self.group))
        self.all_param_names = {name_rule(p) for c in base_commands for p in c.params}
        for cmd in base_commands:
            name, method = self.make_validation_method(cmd)
            setattr(self, name, method)

    def make_validation_method(self, command):
        def param_validation_method(parsed_command):

            counter = collections.Counter(p.data for p in parsed_command.children)

            for param_or_cmd in list(command.params) + list(
                getattr(command, "commands", {}).values()
            ):
                param_or_cmd_id = name_rule(param_or_cmd)
                observed = counter.get(param_or_cmd_id, 0)
                if observed > param_or_cmd.nargs:
                    raise TooManyArgs(param_or_cmd)

        return name_rule(command), param_validation_method


class CLIParsingErrorException(Exception):
    pass


class InvalidInput(CLIParsingErrorException):
    pass


class HelpRequested(Exception):
    pass


class TooManyArgs(CLIParsingErrorException):
    pass


class AmbiguousArgs(CLIParsingErrorException):
    pass


class Transformer(lark.Transformer):
    def __init__(self, *args, group, use_defaults, **kwargs):
        self.group = group
        self.use_defaults = use_defaults
        super().__init__(*args, **kwargs)
        base_commands = list(get_base_commands(self.group))
        self.all_param_names = {name_rule(p) for c in base_commands for p in c.params}
        for cmd in base_commands:
            if isinstance(cmd, CountingCommand) and not isinstance(
                cmd, click.MultiCommand
            ):
                # Not a group
                name, method = self.make_command_method(cmd)
                setattr(self, name, method)
            for param in cmd.params:
                name, method = self.make_param_method(cmd, param)
                setattr(self, name, method)

            if isinstance(cmd, click.MultiCommand):
                name, method = self.make_group_method(cmd)
                setattr(self, name, method)

    def process_params(self, command, parsed):

        d = {}
        for param, value in parsed:

            if param.name == "--help":
                print(command.get_help(click.Context(command)))
                sys.exit()
            if isinstance(param, click.Parameter):
                value = str(value)
            if param.multiple or param.nargs != 1:
                d.setdefault(param, []).append(value)
            else:
                d[param] = value

        out = {}
        for param, value in d.items():
            if isinstance(param, click.Parameter):
                try:
                    out[param.name] = param.process_value(click.Context(command), value)
                except click.exceptions.BadParameter as e:
                    # XXX
                    raise
            elif isinstance(param, click.BaseCommand):

                out[param.name] = {k: v for k, v in value.items() if v != util.UNSET}
            else:
                raise TypeError(param)

        if self.use_defaults:
            for param in command.params:
                if param.name not in out and not param.required:

                    out[param.name] = param.default

        return command, out

    def make_command_method(self, command):

        return (name_rule(command), lambda parsed: self.process_params(command, parsed))

    def make_group_method(self, group):
        def method(parsed):
            import lark

            _group, out = self.process_params(
                group, [(obj, value) for obj, value in parsed]
            )
            return (group, out)

        return name_rule(group), method

    def make_param_method(self, cmd, param):
        def method(parsed):
            if param.is_flag:
                parsed = True
            else:
                [parsed] = parsed

            return (param, parsed)

        return name_rule(param), method


class RemoveInvalidBranches(lark.Transformer):
    def __init__(self, *args, group, **kwargs):
        self.group = group
        super().__init__(*args, **kwargs)
        base_commands = list(get_base_commands(self.group))
        self.all_param_names = {name_rule(p) for c in base_commands for p in c.params}

    def _ambig(self, data):

        trees = [tree for tree in data if check_validity(self.group, tree)]
        if len(trees) == 1:
            return trees[0]

        if len(trees) == 0:
            raise InvalidInput(data)

        trees = [tree for tree in trees if has_help(tree)]

        if not trees:
            raise AmbiguousArgs(data)

        # Pick one.
        return trees[-1]


def has_help(tree):
    return bool(tree.find_data(HELP_COMMAND))


def check_validity(group, tree):
    try:
        Walker(group=group).visit(tree)
    except TooManyArgs:
        return False
    return True


def find_missing_input(parser, s: str) -> t.Optional[t.List[str]]:

    words = shlex.split(s)
    try:
        parser.parse(subprocess.list2cmdline(words))
    except lark.exceptions.ParseError:
        pass
    else:
        return None

    while True:
        try:
            parser.parse(subprocess.list2cmdline(words[:-1]))
        except lark.exceptions.ParseError:
            words = words[:-1]
        else:
            return words


@attr.dataclass
class Parser:
    group: CountingGroup
    callback: t.Callable = lambda **kw: kw
    use_defaults: bool = True
    _id_to_object: t.Dict[str, object] = attr.ib(factory=dict)

    def __attrs_post_init__(self):
        for cmd in get_base_commands(self.group):
            self._id_to_object[name_rule(cmd)] = cmd
            for param in cmd.params:
                self._id_to_object[name_rule(param)] = param

    def parse_string(self, s):
        grammar = build_grammar(self.group)

        parser = lark.Lark(grammar, parser="earley", ambiguity="explicit")
        try:
            tree = parser.parse(s)
        except lark.exceptions.ParseError as e:
            found = find_missing_input(parser, s)
            raise clout.exceptions.MissingInput(self.group, s, found) from e

        try:
            tree = RemoveInvalidBranches(group=self.group).transform(tree)
        except AmbiguousArgs:
            click.echo(
                "The command arguments were ambiguous. Rearranging terms might help."
            )

        transformer = Transformer(group=self.group, use_defaults=self.use_defaults)

        try:
            _group, value = transformer.transform(tree)
        except lark.exceptions.VisitError as e:
            raise e.orig_exc from e

        return value

    def parse_args(self, args: t.List[str]):
        line = subprocess.list2cmdline(args)
        return self.parse_string(line)
