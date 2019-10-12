#!/usr/bin/env python
"""
Styling Strings switching class.

This module will switch between the different behaviours provided
by the longtraceback system, either using the additional StyledString
module to provide its styling, or returning the strings directly.
"""

import os
import sys

import longtraceback.Options


# The module for styled strings - only used when they are configured
StyledStringModule = None


# Internal configuration for whether the styling is set up or not, and how it is configured.
styling_setup = None


# Object we'll use for styled strings
class StyledStringClass(object):
    pass


def StyledString(s, style=None):
    styling = longtraceback.options.styling
    if styling is None or styling == 'none':
        return s

    if styling == 'tokens':
        if style is None:
            return s

        return "<%s>%s</%s>" % (style, s, style)

    if StyledStringModule is None:
        initialise_styling()

    if styling_setup != styling:
        setup_styledstring(styling)

    return StyledStringModule.StyledString(s, style)


def initialise_styling():
    global StyledStringModule   # pylint: disable=global-statement

    # StyledStringClass is clearly defined as a class, globally. It's not clear why pylint complains
    global StyledStringClass    # pylint: disable=global-statement,global-variable-undefined

    path_longtraceback = os.path.dirname(os.path.abspath('__file__'))
    if path_longtraceback not in sys.path:
        sys.path.append(path_longtraceback)
    StyledStringModule = __import__('styledstrings.StyledString').StyledString
    StyledStringClass = StyledStringModule.StyledString

    # There is an __init__, in the parent class, but pylint does not know this because of the
    # runtime import.
    class RenditionTerminal(StyledStringModule.Rendition):  # pylint: disable=no-init
        default_background = 'black'
        default_foreground = 'white'
        colours = {
            'black': 0,
            'red': 1,
            'green': 2,
            'yellow': 3,
            'blue': 4,
            'magenta': 5,
            'cyan': 6,
            'white': 7,
        }
        fg = dict((colour, 30 + value) for colour, value in colours.items())
        bg = dict((colour, 40 + value) for colour, value in colours.items())
        reset = 0
        bold = 1
        underline = 4

        def properties_delta(self, old_properties, new_properties, added, removed, changed): # pylint: disable=W0613
            need_reset = False
            if removed:
                need_reset = True
            if changed:
                if 'bold' in changed:
                    need_reset = True
                if 'underline' in changed:
                    need_reset = True

            codes = []
            if need_reset:
                codes.append(self.reset)
                # The state we're asserting is the new_properties state.
                added = new_properties
            else:
                # We are just adding or changing something.
                # We can accumulate the 'new' settings from changed into added, to give the complete set.
                added.update(dict((name, new_value) for name, (_, new_value) in changed))

            if 'bold' in added:
                codes.append(self.bold)
            if 'underline' in added:
                codes.append(self.underline)
            if 'fg' in added:
                codes.append(self.fg[added['fg']])
            if 'bg' in added:
                codes.append(self.bg[added['bg']])

            if not codes:
                return []

            return ["\x1b[%sm" % (';'.join(str(code) for code in codes))]

    StyledStringModule.RenditionTerminal = RenditionTerminal


def setup_styledstring(styling):
    global styling_setup  # pylint: disable=global-statement
    styling_setup = styling
    if styling == 'identity':
        StyledStringModule.StyledString.render_class = StyledStringModule.RenditionIdentity
        return

    # Configure the style names that we use and the colours
    used_style_names = [
        '.context',
        '.context-caret',
        '.exception-name',
        '.exception-message',
        '.extensions.info',
        '.filename',
        '.frame-repeated',
        '.function-name',
        '.function-type',
        '.header',
        '.header.cause',
        '.header.context',
        '.header.exception',
        '.header.file',
        '.header.locals',
        '.header.parameters',
        '.header.extensions.info',
        '.header.traceback',
        '.internal-exception',
        '.line-divider',
        '.line-exception',
        '.lineno',
        '.line-number',
        '.local',
        '.parameter',
        '.parameter-sequence',
        '.processing',
        '.property',
        '.prototype-parameters',
        '.sequence-values',
        '.source',
        '.traceheader',
        '.varname',
        '.varvalue',
    ]

    if styling == 'markup':
        StyledStringModule.StyledString.render_class = StyledStringModule.RenditionExampleMarkup

        for style in used_style_names:
            rule = StyledStringModule.Rule(style, {style[1:]: None})
            StyledStringModule.StyledString.style_rules.add_rule(rule)

    elif styling == 'terminal' or styling == 'ansi':
        # Our terminal rendering
        StyledStringModule.StyledString.render_class = StyledStringModule.RenditionTerminal

        for style in longtraceback.options.styling_colours:
            rule = StyledStringModule.Rule(style, longtraceback.options.styling_colours.get(style, {}))
            StyledStringModule.StyledString.style_rules.add_rule(rule)

    else:
        raise RuntimeError("Undefined LongTraceback styling '%s'" % (styling))
