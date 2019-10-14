from .base import BaseTerminal
from .exceptions import UnsupportedAttributeException
from .exceptions import UnsupportedColorException
from ..style import Color, Style


class NoColorTerminal(BaseTerminal):
    """
    Base terminal with no colors at all
    """

    def __init__(self):
        self.supported_attrs = []
        self.supported_colors = [Color()]

    def setup(self, appstate):
        pass

    def teardown(self, appstate):
        pass

    def configure_style(self, style):
        # "any color you like"
        return Style()

    def assert_compatible_color(self, color):
        if color not in self.supported_colors:
            msg = "color unsupported in this terminal: rgb{clr}".format(
                clr=color.rgb
            )
            raise UnsupportedColorException(msg)

    def assert_compatible_attrs(self, attrs):
        for attr in attrs:
            if attr not in self.supported_attrs:
                msg = "attr unsupported in this terminal: '{attr}'".format(
                    attr=attr
                )
                raise UnsupportedAttributeException(msg)

    def _build_fg_codes(self, fg_color):
        return []

    def _build_bg_codes(self, bg_color):
        return []

    def _build_attr_codes(self, attrs):
        return []

    def _build_reset_sequence(self):
        return []

    def test(self):
        lines = ["~Lilies~", "Terminal test: No Color"]
        lines.append("")
        lines.append("All attributes disabled, nothing to show!")
        print("\n".join(lines))
