import functools
import os
import sys
import typing as t

import attr
import click
import desert
import glom
import inflection
import lark
import marshmallow
import typing_inspect

import clout.exceptions

from .. import util
from . import parsing


NO_DEFAULT = "__NO_DEFAULT__"
TOP_LEVEL_NAME = "top_level_name"
NoneType = type(None)


def is_python_syntax(s: str) -> bool:
    import black

    try:
        black.format_str(s, 88)
    except black.InvalidInput:
        return False
    return True


def pythonify(obj):
    if is_python_syntax(repr(obj)):
        return repr(obj)
    if callable(obj) and is_python_syntax(obj.__name__):
        return obj.__name__
    return "..."


class Debug:
    def __repr__(self):
        import black

        pairs = ", ".join(
            (
                f"{k}={pythonify(v)}"
                for k, v in vars(self).items()
                if not k.startswith("_")
            )
        )
        name = type(self).__name__
        return black.format_str(f"{name}({pairs})", line_length=88)


class Option(Debug, click.Option):
    pass


class Group(Debug, parsing.CountingGroup):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs, standalone_mode=False)
        except SystemExit as e:
            if e.code != 0:
                raise


class DebuggableCommand(Debug, parsing.CountingCommand):
    def __call__(self, *args, **kwargs):
        try:
            return super().__call__(*args, **kwargs)
        except SystemExit as e:
            if e.code != 0:
                raise


class MarshmallowFieldParam(click.ParamType):
    def __init__(self, field):
        self.field = field

    @property
    def name(self):
        return type(self.field).__name__.split(".")[-1]

    def convert(self, value, param, ctx):

        try:
            return self.field.deserialize(value)
        except marshmallow.exceptions.ValidationError as e:
            raise click.BadParameter(ctx=ctx, param=param, message=str(e)) from e


MM_TO_CLICK = {
    marshmallow.fields.String: click.STRING,
    marshmallow.fields.Int: click.INT,
    marshmallow.fields.Float: click.FLOAT,
    marshmallow.fields.Raw: click.STRING,
    marshmallow.fields.Bool: click.BOOL,
}


def make_help_command():
    return DebuggableCommand(name="--help", hidden=True)


@functools.singledispatch
def make_param_from_field(
    field: marshmallow.fields.Field, data, default
) -> click.Parameter:

    if data:

        data = data.copy()
        if "type" not in data:
            data["type"] = MM_TO_CLICK[type(field)]

        return Option(show_default=True, **data)

    return Option(
        ["--" + field.name],
        type=MarshmallowFieldParam(field),
        required=False,
        default=default,
        show_default=True,
    )


@make_param_from_field.register(marshmallow.fields.Boolean)
def _(field: marshmallow.fields.Boolean, data, default) -> Option:

    if data:
        return Option(**data, default=default)

    return Option(
        [util.dasherize(f"--{field.name}/--no-{field.name}")],
        default=default,
        required=field.missing == marshmallow.missing,
        is_flag=True,
        show_default=True,
    )


@make_param_from_field.register(marshmallow.fields.String)
@make_param_from_field.register(marshmallow.fields.Int)
@make_param_from_field.register(marshmallow.fields.Float)
@make_param_from_field.register(marshmallow.fields.Date)
@make_param_from_field.register(marshmallow.fields.DateTime)
@make_param_from_field.register(marshmallow.fields.Raw)
def _(field, data, default) -> Option:
    if data:
        data = data.copy()
        if "type" not in data:
            data["type"] = MM_TO_CLICK[type(field)]
        return Option(show_default=True, **data, default=default)
    param_type = MM_TO_CLICK[type(field)]
    return Option(
        ["--" + field.name], type=param_type, show_default=True, default=default
    )


def extract(mapping, path):
    for entry in path:
        mapping = mapping[entry]
    return mapping


def get_default(field, path, default_map):

    try:
        return extract(default_map, path[1:])
    except KeyError:
        return field.default


@attr.dataclass(frozen=True)
class CLI:
    context_settings: t.Dict[str, t.Any] = attr.ib(factory=dict)
    inherits: t.FrozenSet[str] = frozenset({"app_name"})
    metadata_key: str = "cli"
    args: t.List[str] = attr.ib(factory=list)
    app_name: t.Optional[str] = None

    def make_command_from_schema(
        self, schema: marshmallow.Schema, path: t.Sequence[str]
    ) -> click.BaseCommand:
        params = []
        commands = []
        # import pudb; pudb.set_trace()
        for field in schema.fields.values():
            if isinstance(field, marshmallow.fields.Nested):
                commands.append(
                    self.make_command_from_schema(
                        field.schema, path=path + (field.name,)
                    )
                )
            elif isinstance(field, marshmallow.fields.Field):
                user_specified = field.metadata.get("cli")
                default = get_default(
                    field,
                    path=path + (field.name,),
                    default_map=self.context_settings.get("default_map", {}),
                )

                if isinstance(field.metadata.get("cli"), click.Parameter):
                    param = field.metadata["cli"]
                else:
                    param = make_param_from_field(
                        field, user_specified, default=default
                    )

                params.append(param)
            else:
                raise TypeError(field)

        commands.append(make_help_command())

        help = getattr(schema, "help", None)
        if commands:
            return Group(
                name=path[-1],
                commands={c.name: c for c in commands},
                params=params,
                chain=True,
                result_callback=lambda *a, **kw: (a, kw),
                help=help,
                short_help=help,
                context_settings=self.context_settings,
            )
        return DebuggableCommand(
            name=path[-1],
            params=params,
            callback=identity,
            help=help,
            short_help=help,
            context_settings=self.context_settings,
        )

    def get_command(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):
        metadata = metadata or {}

        cli_metadata: t.Union[
            t.Dict[str, t.Any], click.BaseCommand, click.Parameter
        ] = metadata.get(self.metadata_key, None)
        if isinstance(cli_metadata, (click.BaseCommand, click.Parameter)):
            command = cli_metadata
        else:

            name = metadata.get("name", util.dasherize(self.app_name))

            schema = desert.schema_class(typ)()
            command = self.make_command_from_schema(schema, path=(name,))

            def schema_load(*a, **kw):
                try:
                    return schema.load(*a, **kw)
                except marshmallow.exceptions.ValidationError as e:
                    raise clout.exceptions.ValidationError(*e.args) from e

            command.callback = schema_load

        command = Group(
            name=TOP_LEVEL_NAME,
            commands={c.name: c for c in [command, make_help_command()]},
            callback=command.callback,
        )
        return command

    def prep(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):

        command = self.get_command(typ, default, metadata, args)

        parser = parsing.Parser(command, callback=command.callback, use_defaults=True)
        cli_args = (TOP_LEVEL_NAME,) + tuple(args or self.args or sys.argv[1:])

        try:
            result = parser.parse_args(cli_args)
        except click.exceptions.BadParameter as e:
            e.show()
            sys.exit(1)
        except (
            lark.exceptions.ParseError,
            lark.exceptions.UnexpectedCharacters,
            lark.exceptions.VisitError,
        ):

            print(command.get_help(click.Context(command)) + EPILOG)
            if int(os.environ.get("CLI_SHOW_TRACEBACK", 0)):
                raise
            else:
                sys.exit(1)
        except clout.exceptions.MissingInput as e:
            result = parser.parse_args(e.found + ["--help"])

        [value] = result.values()
        return value

    def build(
        self,
        typ: t.Type,
        default=NO_DEFAULT,
        metadata: t.Mapping[str, t.Any] = None,
        args=(),
    ):

        command = self.get_command(typ, default, metadata, args)

        result = command.callback(self.prep(typ, default, metadata, args))

        return result

    def set(self, **kw):
        return attr.evolve(self, **kw)


class NonStandaloneCommand(click.Command):
    def main(self, *a, standalone_mode=False, **kw):
        return super().main(*a, standalone_mode=standalone_mode, **kw)


EPILOG = "\n\nNote:\n  export CLI_SHOW_TRACEBACK=1 to show traceback on error.\n"


class Command(click.Command):
    def __init__(
        self,
        name=None,
        type=None,
        *a,
        app_name=None,
        callback=lambda x: x,
        params=None,
        context_settings=None,
        epilog=None,
        **kw,
    ):
        if type is None:
            raise TypeError("missing `type` argument")
        self.app_name = app_name

        epilog = epilog or ""
        epilog += EPILOG

        context_settings = context_settings or {}
        context_settings["ignore_unknown_options"] = True
        super().__init__(
            name=name,
            *a,
            **kw,
            add_help_option=False,
            epilog=epilog,
            context_settings=context_settings,
        )
        self.params = (params or []) + [
            click.Argument(["args"], type=click.UNPROCESSED, nargs=-1)
        ]
        self.callback = lambda args: callback(
            CLI(
                app_name=app_name or util.dasherize(type.__name__),
                context_settings=context_settings,
            ).build(type, args=args)
        )

    def build(self, *a, **kw):
        return self.main(standalone_mode=False)
