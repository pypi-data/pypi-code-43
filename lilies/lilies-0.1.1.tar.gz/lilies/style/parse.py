from future.utils import string_types
from . import colors
from .palette import get_color
from .styles import Style


class InvalidStyleError(Exception):
    pass


ATTRIBUTE_NAME_MAP = {
    "bold": "bold",
    "strong": "bold",
    "bright": "bold",
    "dim": "dim",
    "italic": "italic",
    "strike": "strike",
    "strikethrough": "strike",
    "struck": "strike",
    "struckthrough": "strike",
    "underlined": "underline",
    "underline": "underline",
    "underscore": "underline",
    "underscored": "underline",
    "blink": "blink",
    "flash": "blink",
}


def _strip_all(itr):
    return list(map(lambda s: s.strip(), itr))


def _is_attr(name):
    return name in ATTRIBUTE_NAME_MAP


def _translate_attr(attr):
    return ATTRIBUTE_NAME_MAP[attr]


def parse_style(style):
    if style is None:
        return Style()

    return _parse_style_str(style)


def _parse_style_str(style):
    """
    parses style as a style string.
    Format:
    comma, separated, attributes FG_COLOR on BG_COLOR

    Examples:

    Bold, underlined, red text on a black background
    bold, underlined red on black

    Red text on blue background:
    red on blue

    Green text:
    green

    Normal text on a white background:
    on white
    """
    if not isinstance(style, (string_types,)):
        raise InvalidStyleError("Expected a string type")
    # Step 1: split out attributes with commas
    # and clean components for whitespace
    step1 = style.split(",")
    step1 = _strip_all(step1)

    # at this point, we have all but the last attribute
    # parted out, with the rest of we need to parse on
    # the right.
    attrs = step1[:-1]
    step1 = step1[-1]
    for attr in attrs:
        if not _is_attr(attr):
            raise InvalidStyleError(
                "Expected attribute: {attr}".format(attr=attr)
            )

    # Step 2: Let's try to pull the last attribute out
    # by splitting by word, and testing the first word.
    # If it's not an attribute, we should have no attributes.
    # Otherwise, someone input something like this:
    # bold, on green
    step2 = step1.split()
    step2 = _strip_all(step2)
    has_attr = len(step2) > 0 and _is_attr(step2[0])
    expect_no_attributes = len(step2) > 1 and not has_attr
    if expect_no_attributes and len(attrs) > 0:
        raise InvalidStyleError("Unexpected comma")
    if has_attr:
        attrs.append(step2[0])
        # remove the attribute from our set, we're done with it
        step2 = step2[1:]
    # we allow for some aliases, so this will unalias them
    attrs = list(map(_translate_attr, attrs))

    # Step 3: We need to part out a background color if
    # it exists. This is entirely dependent on the 'on' keyword.
    # Reminder that step2 at this point is still a list.
    if "on" in step2:
        ix = step2.index("on")
        bg_str = "".join(step2[ix + 1 :])
        bg_str = _clean_colorname(bg_str)
        bg = get_color(bg_str)
        if not bg:
            raise InvalidStyleError(
                "Invalid background color: {bg}".format(bg=bg_str)
            )
        # Step 3 should now be JUST a foreground color.
        step4 = "".join(step2[:ix])
    else:
        # Use default color
        bg = colors.Color()
        step4 = "".join(step2)

    # Step 4:
    # All that should be left at this point is the fg color.
    # Since we allow empty color names to be 'default',
    # account for that as well.
    fg_str = _clean_colorname(step4)
    if len(fg_str) == 0:
        fg = colors.Color()
    else:
        fg = get_color(fg_str)
        if not fg:
            raise InvalidStyleError(
                "Invalid foreground color: {fg}".format(fg=fg_str)
            )

    # All done
    return Style(fg, bg, attrs)


def _clean_colorname(name):
    # We accept camelCase, snake_case,
    # spaces, whatever formatting people like.

    if len(name) > 30:
        return ""
    name = name.strip()
    unsnaked = "".join(name.split("_"))
    condensed = "".join(unsnaked.split())
    return condensed.lower()
