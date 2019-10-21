from pacurses.constants.sink_types import SinkTypes
from pacurses.pulse_audio.input import Input
from pacurses.pulse_audio.output import Output


def get_sink_type(sink):
    if isinstance(sink, Output):
        return SinkTypes.OUTPUT

    elif isinstance(sink, Input):
        return SinkTypes.INPUT

    else:
        raise Exception(
            f"Was not able to detect the SinkType for the sink {sink}!"
        )
