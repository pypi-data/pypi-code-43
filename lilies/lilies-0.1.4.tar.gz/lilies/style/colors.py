from builtins import object
import colorsys


def rgb_to_hsl(r, g, b):
    r_ratio = r / 255.0
    g_ratio = g / 255.0
    b_ratio = b / 255.0

    hsl_ratios = colorsys.rgb_to_hls(r_ratio, g_ratio, b_ratio)
    return (hsl_ratios[0] * 360, hsl_ratios[2] * 100, hsl_ratios[1] * 100)


def hsl_to_rgb(h, s, l):
    h_ratio = h / 360.0
    l_ratio = l / 100.0
    s_ratio = s / 100.0

    rgb_ratios = colorsys.hls_to_rgb(h_ratio, l_ratio, s_ratio)
    return tuple(map(lambda n: int(round(n * 255)), rgb_ratios))


class Color(object):
    def __init__(self, rgb=None, hsl=None):
        if rgb is None and hsl is None:
            # This is considered "NO COLOR"
            # and is the default console color.
            self.rgb = None
            self.hsl = None
            return
        if rgb is None:
            rgb = hsl_to_rgb(*hsl)
        if hsl is None:
            hsl = rgb_to_hsl(*rgb)
        self.rgb = rgb
        self.hsl = hsl

    def isreset(self):
        return self.rgb is None and self.hsl is None

    def __hash__(self):
        # This is a hack to make sure that None is not the same
        # as an undefined color.
        if self.rgb is None:
            return hash("default")
        return hash(self.rgb)

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
