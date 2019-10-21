from urwid import Divider, Pile, Text

from pacurses.constants.palette_names import PaletteNames
from pacurses.constants.sink_types import SinkTypes
from pacurses.gui.abbreviation import abbreviate_sink
from pacurses.pulse_audio.information import Information

MAPPING_OPERATOR_STRING = " -> "


class Status(Pile):
    def __init__(self, width):
        info = Information()
        length = width - 3

        def get_output_text(output):
            return abbreviate_sink(
                output, SinkTypes.OUTPUT, length, with_state=True
            )

        def get_input_text(input):
            return abbreviate_sink(
                input, SinkTypes.INPUT, length, with_state=True
            )

        rows = []
        rows.append(Text((PaletteNames.UNDERLINE, "Outputs:")))
        rows.extend(
            [
                Text(f" {get_output_text(output)}")
                for output in info.output_list
            ]
        )

        rows.append(Divider())
        rows.append(Text((PaletteNames.UNDERLINE, "Inputs:")))
        rows.extend(
            [Text(f" {get_input_text(input)}") for input in info.input_list]
        )

        rows.append(Divider())
        rows.append(Text((PaletteNames.UNDERLINE, "Mapping:")))

        rows.extend(
            [
                Text(
                    " {0}{1}{2}".format(
                        input.index,
                        MAPPING_OPERATOR_STRING,
                        input.mapped_output_index,
                    )
                )
                for input in info.input_list
            ]
        )

        super(Status, self).__init__(rows)
