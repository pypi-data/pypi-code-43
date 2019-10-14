from ..style import Style


class LilyStringCompiler(object):
    """
    A compiler object that will take a series of
    LilyStringPieces and compile them to display
    in a particular terminal. Designed to 'just work'
    even when the colors/styles used are not fully
    supported within the terminal environment chosen.
    """

    def __init__(self, terminal):
        self.term = terminal

    def compile(self, pieces):
        compiled_parts = []
        previous_style = Style()
        for piece in pieces:
            cur_style = self.term.configure_style(piece.style)
            diff = cur_style.diff(previous_style)
            previous_style = cur_style
            compiled_parts.append(self.term.encode_sequence(diff))
            compiled_parts.append(piece.text)
        # reset
        diff = Style().diff(previous_style)
        compiled_parts.append(self.term.encode_sequence(diff))
        return "".join(compiled_parts)
