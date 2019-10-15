from . import ansicodes
from ..style import Style


class AnsiAttributesMixin(object):
    """
    Adds functionality to detect and encode standard
    ansi style attributes, must also extend Ansi8Terminal
    or a subclass for this to work.
    """

    def _build_attr_codes(self, attrs):
        on_codes = []
        off_codes = []
        bold_dim_off = False
        # Bold and Dim have the same off char.
        # This char should come FIRST, and then
        # other chars can go after to build up
        # the rest of the sequence.
        for attr in attrs:
            if attrs[attr]:
                on_codes.append(self._attr_on_code(attr))
            else:
                if attr not in ["bold", "dim"]:
                    off_codes.append(self._attr_off_code(attr))
                elif not bold_dim_off:
                    # Bold and Dim have the same off char.
                    # Make sure we only add one.
                    off_codes.append(self._attr_off_code(attr))
                    bold_dim_off = True
        return off_codes + on_codes

    def _attr_on_code(self, attr):
        return ansicodes.ATTR_ON_CODES[attr]

    def _attr_off_code(self, attr):
        return ansicodes.ATTR_OFF_CODES[attr]

    def test_attributes(self):
        if len(self.supported_attrs) == 0:
            return

        lines = ["Supported styles:"]
        attr_strs = []
        no_style = Style(attrs=[])
        for attr in self.supported_attrs:
            cur_style = Style(attrs=[attr])
            diff = cur_style.diff(no_style)
            ansi = self.encode_sequence(diff)
            attr_strs.append(
                "{ansi}{attr}{reset}".format(
                    ansi=ansi, attr=attr, reset="\033[0m"
                )
            )
        lines.append("  ".join(attr_strs))
        print("\n".join(lines))
