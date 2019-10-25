from datetime import datetime

from janis_core import ToolInput, ToolOutput, Stdout, Array, File, ToolMetadata, Boolean
from .unixtool import UnixTool


class Cat(UnixTool):
    @staticmethod
    def tool():
        return "cat"

    def friendly_name(self):
        return "Concatenate"

    @staticmethod
    def base_command():
        return "cat"

    def inputs(self):
        return [
            ToolInput("file", File(optional=True)),
            ToolInput("files", Array(File(), optional=True), position=1),
            ToolInput(
                "number_output",
                Boolean(optional=True),
                prefix="-n",
                doc="Number the output lines, starting at 1.",
            ),
            ToolInput(
                "number_non_blank",
                Boolean(optional=True),
                prefix="-b",
                doc="Number the non-blank output lines, starting at 1.",
            ),
            ToolInput(
                "disable_output_buffer",
                Boolean(optional=True),
                prefix="-u",
                doc="Disable output buffering.",
            ),
            ToolInput(
                "squeeze",
                Boolean(optional=True),
                prefix="-s",
                doc="Squeeze multiple adjacent empty lines, causing the output to be single spaced.",
            ),
            ToolInput(
                "display_nonprint_chars",
                Boolean(optional=True),
                prefix="-e",
                doc="Display non-printing characters (see the -v option), and display "
                "a dollar sign (`$') at the end of each line.",
            ),
            ToolInput(
                "display_non",
                Boolean(optional=True),
                prefix="-t",
                doc="Display non-printing characters (see the -v option), and display tab characters as `^I'.",
            ),
            ToolInput(
                "number_non_blank",
                Boolean(optional=True),
                prefix="-v",
                doc="Display non-printing characters so they are visible.  Control characters print as `^X' for "
                "control-X; the delete character (octal 0177) prints as `^?'.  Non-ASCII characters (with the"
                " high bit set) are printed as `M-' (for meta) followed by the character for the low 7 bits.",
            ),
        ]

    def outputs(self):
        return [ToolOutput("out", Stdout())]

    def bind_metadata(self):

        self.metadata.dateUpdated = datetime(2019, 7, 26)
        self.metadata.documentation = """\
The cat utility reads files sequentially, writing them to the standard output. The file operands are processed in \
command-line order. If file is a single dash (`-') or absent,cat reads from the standard input. If file is a UNIX \
domain socket, cat connects to it and then reads it until EOF. This complements the UNIX domain binding capability \
available in inetd(8)."""
