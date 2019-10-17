from prompt_toolkit.contrib.regular_languages import compile
from prompt_toolkit.document import Document
from prompt_toolkit.application.current import get_app

from coderadio.log import logger

from coderadio.buffers import list_buffer
from coderadio.buffers import help_buffer

from coderadio.player import radio


COMMAND_GRAMMAR = compile(
    r"""(
        (?P<command>[^\s]+) \s+ (?P<subcommand>[^\s]+) \s+ (?P<term>[^\s].+) |
        (?P<command>[^\s]+) \s+ (?P<term>[^\s]+) |
        (?P<command>[^\s!]+)
    )"""
)

COMMAND_TO_HANDLER = {}


def has_command_handler(command):
    return command in COMMAND_TO_HANDLER


def call_command_handler(command, **kwargs):
    COMMAND_TO_HANDLER[command](**kwargs)


def get_commands():
    return COMMAND_TO_HANDLER.keys()


def get_command_help(command):
    return COMMAND_TO_HANDLER[command].__doc__


def handle_command(event, **kwargs):
    # logger.info(event.current_buffer.name)
    # logger.info(event.current_buffer.text)

    # handles command_prompt event (buffer)
    if event.current_buffer.name == "command_buffer":

        # !!!!! get string from buffer
        input_string = event.current_buffer.text
        # valid command
        match = COMMAND_GRAMMAR.match(input_string)

        if match is None:
            return

        # grammar post processing
        variables = match.variables()
        command = variables.get("command")
        kwargs.update({"variables": variables, "event": event})

        if has_command_handler(command):
            call_command_handler(command, **kwargs)

    # handles list_view event!!!!
    # list_view sends in kwargs the text of the row
    # that was requested with enter or click inside ListView widget.
    if event.current_buffer.name == "list_buffer":
        call_command_handler("play", **kwargs)


def cmd(name):
    """
    Decorator to register commands in this namespace
    """

    def decorator(func):
        COMMAND_TO_HANDLER[name] = func

    return decorator


@cmd("exit")
def exit(**kwargs):
    """ exit Ctrl + Q"""
    get_app().exit()


@cmd("play")
def play(**kwargs):

    if "text" in kwargs:
        text = kwargs.get("text")
        command = "byid"
        term = text.split("|")[0].strip()
    else:
        variables = kwargs.get("variables")
        command = variables.get("subcommand")
        term = variables.get("term")

    radio.play(command=command, term=term)
    


@cmd("stop")
def stop(**kwargs):
    """ exit Ctrl + S"""
    # TODO: implement stop shortcut
    radio.stop()


@cmd("list")
def stations(**kwargs):
    subcommand = kwargs["variables"].get("subcommand")
    term = kwargs["variables"].get("term")
    content = radio.list(command=subcommand, term=term)
    list_buffer.reset(Document(content, 0))


@cmd("pin")
def pin(**kwargs):
    """bookmark radio station and hang on homepage"""
    # TODO:
    pass


@cmd("rec")
def stations(**kwrags):
    """records a radio station in the background"""
    # TODO:
    logger.info(kwrags)


@cmd("info")
def info(**kwargs):
    """ show info about station """
    pass


@cmd("help")
def help(**kwargs):
    """ show help """
    get_app().layout.focus(help_buffer)
