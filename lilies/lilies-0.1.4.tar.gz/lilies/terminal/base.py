from builtins import object
from abc import ABCMeta, abstractmethod
from future.utils import with_metaclass

from . import ansicodes


class BaseTerminal(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def setup(self, appstate):
        raise NotImplementedError("setup")

    @abstractmethod
    def teardown(self, appstate):
        raise NotImplementedError("teardown")

    def assert_compatible_stylediff(self, style_diff):
        if style_diff.fg is not None:
            self.assert_compatible_color(style_diff.fg)
        if style_diff.bg is not None:
            self.assert_compatible_color(style_diff.bg)
        self.assert_compatible_attrs(style_diff.attrs.keys())

    @abstractmethod
    def configure_style(self, style):
        raise NotImplementedError("configure_style")

    @abstractmethod
    def assert_compatible_color(self, color):
        raise NotImplementedError("assert_compatible_color")

    @abstractmethod
    def assert_compatible_attrs(self, attrs):
        raise NotImplementedError("assert_compatible_attrs")

    @abstractmethod
    def _build_fg_codes(self, fg_color):
        raise NotImplementedError("_build_fg_codes")

    @abstractmethod
    def _build_bg_codes(self, bg_color):
        raise NotImplementedError("_build_bg_codes")

    @abstractmethod
    def _build_attr_codes(self, attrs):
        raise NotImplementedError("_build_attr_codes")

    @abstractmethod
    def test(self):
        raise NotImplementedError("test")

    @abstractmethod
    def _build_reset_sequence(self):
        raise NotImplementedError("_build_reset_sequence")

    def encode_sequence(self, style_diff):
        self.assert_compatible_stylediff(style_diff)
        if style_diff.isreset():
            return "".join(self._build_reset_sequence())
        fg_codes = self._build_fg_codes(style_diff.fg)
        bg_codes = self._build_bg_codes(style_diff.bg)
        attr_codes = self._build_attr_codes(style_diff.attrs)
        fg_seq = "".join(map(ansicodes.esc, fg_codes))
        bg_seq = "".join(map(ansicodes.esc, bg_codes))
        attr_chars = map(ansicodes.esc, attr_codes)
        attr_seq = "".join(attr_chars)
        return attr_seq + fg_seq + bg_seq
