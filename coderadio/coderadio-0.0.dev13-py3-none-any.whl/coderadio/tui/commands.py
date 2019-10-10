from numbers import Number

from prompt_toolkit.contrib.regular_languages import compile
from prompt_toolkit.document import Document
from prompt_toolkit.application.current import get_app

from coderadio.core.log import logger
from coderadio.core.classes import radios
from coderadio.core.classes import radio_browser
from coderadio.core.classes import Station
from coderadio.core.player import Stop

from coderadio.core.buffers import list_buffer
from coderadio.core.buffers import help_buffer

from coderadio.core.exchange import display_now
from coderadio.core.exchange import play_now


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
    # list_view is not buffer.
    # list_view sends in kwargs the index of the row
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
    def get_playable_station():
        # TODO
        pass

    index = kwargs.get("index", None)

    # play the radio station from list_view
    if isinstance(index, Number):
        obj = radios.get_obj(kwargs.get("index"))
    else:
        # play the radio station from command_prompt
        variables = kwargs.get("variables")
        command = "{}_{}".format("stations", variables.get("subcommand"))
        term = variables.get("term")
        data = getattr(radio_browser, command)(term)
        obj = Station(**data[0])

    play_now.put(obj)
    display_now.put(obj.show_info())
    logger.info("playing...")


@cmd("stop")
def stop(**kwargs):
    """ exit Ctrl + S"""
    # TODO: implement shortcut key to stop playing
    play_now.put(Stop())


@cmd("bytag")
def bytag(**kwargs):
    variables = kwargs.get("variables")
    term = variables.get("term")
    radios.data = radio_browser.stations_bytag(term)
    list_buffer.reset(Document(radios.content, 0))


@cmd("stations")
def stations(**kwargs):

    variables = kwargs.get("variables")
    command = "{}_{}".format(
        variables.get("command"), variables.get("subcommand")
    )
    term = variables.get("term")
    radios.data = getattr(radio_browser, command)(term)
    list_buffer.reset(Document(radios.content, 0))


@cmd("list")
def stations(**kwargs):
    variables = kwargs.get("variables")
    command = "{}_{}".format(
        variables.get("command"), variables.get("subcommand")
    )
    term = variables.get("term")
    command = (
        "stations_" + command.split("_")[1]
    )  # stations_bytag -> list_bytag
    radios.data = getattr(radio_browser, command)(term)
    list_buffer.reset(Document(radios.content, 0))


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
