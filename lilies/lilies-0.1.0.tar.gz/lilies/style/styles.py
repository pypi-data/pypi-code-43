from .colors import Color


MATCH = "__match__"


class StyleDiff(object):
    def __init__(self, fg=None, bg=None, attrs={}, full_reset=False):
        self.fg = fg
        self.bg = bg
        self.attrs = attrs

        # Full reset overrides all other style changes in favor of
        # a complete reset to defaults. This helps favor the full
        # ANSI reset character, \033[0m, which is cleaner on average.
        self._full_reset = full_reset

    def isreset(self):
        return self._full_reset


class Style(object):
    def __init__(self, fg=Color(), bg=Color(), attrs=[]):
        self.fg = fg
        self.bg = bg
        self.attrs = list(attrs)

    def diff(self, previous):
        if self.is_default() and not previous.is_default():
            return StyleDiff(full_reset=True)
        fg_diff = None
        bg_diff = None
        if self.fg != previous.fg:
            fg_diff = self.fg
        if self.bg != previous.bg:
            bg_diff = self.bg
        these_attrs = set(self.attrs)
        those_attrs = set(previous.attrs)
        new_attrs = these_attrs - those_attrs
        removed_attrs = those_attrs - these_attrs
        attrs_diff = {}
        for attr in new_attrs:
            attrs_diff[attr] = True
        for attr in removed_attrs:
            attrs_diff[attr] = False
        return StyleDiff(fg_diff, bg_diff, attrs_diff)

    def is_default(self):
        return self.fg == Color() and self.bg == Color() and self.attrs == []

    def __hash__(self):
        components = (hash(self.fg), hash(self.bg), tuple(self.attrs))
        return hash(components)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
