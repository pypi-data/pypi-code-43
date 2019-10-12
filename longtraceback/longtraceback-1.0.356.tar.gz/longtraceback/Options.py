#!/usr/bin/env python
"""
Configuration for the LongTraceback system.
"""

# pylint: disable=bad-continuation

import inspect
import os.path
import sys
import tokenize
import types


try:
    # Python 2
    import ConfigParser as configparser
except ImportError:
    # Python 3
    import configparser  # pylint: disable=import-error


# Allow us to capture using cStringIO if we have it, or the pure python StringIO.
# May allow us to function on non-CPython systems.
IOClass = None
try:
    import cStringIO
    IOClass = cStringIO
except ImportError:
    import io
    IOClass = io


class LongTracebackOptions(object):
    """
    Container for the options we handle in the traceback.
    """
    _parameters = None
    _settings_from_config = []
    _colour_from_config = False

    def __init__(self):
        """
        Options for the 'longtraceback' system.
        """

        # How many lines of context to show in traceback
        self.line_context = 4

        # A function to call to determine whether a frame is ignored.
        # This is the simple handler for frame filtering.
        self.ignore_frame = lambda _: False

        # A function to filter the frames to remove relative elements.
        # Takes a list of traceback frames and returns a filtered list.
        self.filter_frames = self.default_filter_frames

        # Whether we report on failures to produce variable output
        self.debug_vars = True

        # Whether our parameters to functions are inline or separated out
        # 'none'     : parameters are not shown inline, eg 'myfunc'
        # 'inline'   : parameters are shown inline, eg 'myfunc(self=<foo>, bar=7)'
        # 'prototype': parameters are given just by keyword, eg 'myfunc(self, bar)'
        self.params_inline = 'none'

        # Whether we hide the instance and object ids
        self.hide_instance_ids = True

        # Whether we show simple properties of objects.
        self.show_simple_object_properties = True

        # Which members of which builtin objects will be displayed.
        # The key's presence indicates that we will include members for that builtin.
        # The value may be None (to just display default members, or an iterable containing
        # a list of elements that we force the display of.
        self.formatable_builtin_members = {
            'functools.partial': ('func', 'args', 'keywords'),
            '_sre.SRE_Pattern': ('pattern', 'flags'),
            '_sre.SRE_Match': ('pos', 'endpos')
        }

        # Whether we show the function type in the name of the function
        self.show_function_type = False

        # Whether we show an indication of whether variables have changed since function entry
        self.show_changed_variables = False

        # Whether we place a blank line between stack frames
        self.blank_line_between_frames = True

        # Whether we recognise repetition in the frames
        self.recognise_repetitions = True

        # Whether we try to show parameters on repetitions
        self.show_parameter_changes_on_repetitions = True

        # Whether we use the experimental repr patching
        self.experimental_repr = False

        # The limits on the string formatting
        self.string_max_len = 1024 * 4
        self.string_max_lines = 8

        # The limits on non-string formatting
        self.value_max_len = 1024 * 4

        # Whether our extensions are enabled
        self.enable = True
        self.enable_format = True
        self.enable_extract = True

        # Whether we will report internal exceptions whilst running the trace
        self.internal_traceback = True

        # Whether we will use the experimental 'ValueFormat'
        self.new_value_formatter = False

        # Whether we include a header on parameters and locals in the traceback
        self.header_on_parameters = False
        self.header_on_locals = True


        ##
        # Messages for the start of the traceback
        self.start_message = "Traceback (most recent call last):"

        ##
        # Messages generated for the Python 3 chained exceptions
        self.cause_message = "The above exception was the direct cause " \
                             "of the following exception:"
        self.context_message = "During handling of the above exception, " \
                               "another exception occurred:"

        ##
        # Messages for the headers within the frame
        self.parameters_message = "Parameters:"
        self.locals_message = "Locals:"

        ##
        # Message for repeated frames
        self.frame_repetition_message = "... Prior frame repeated {} times ..."


        ##
        # What styling we should apply
        #   'none' - no styling; all processed strings are actually strings
        #   'tokens' - token names (but still plain strings)
        #   'identity' - no styling; all processed strings are StyledStrings
        #   'markup' - markup-style strings
        #   'terminal', 'ansi' - coloured strings
        self.styling = 'ansi'

        ##
        # Colouring to apply as style in 'terminal' styling
        # A dictionary keyed by the names of the context, the values are a
        # dictionary which may contain:
        #   'fg' - the foreground colour to use (8 ANSI colours), or None to clear
        #   'bg' - the background colour to use (8 ANSI colours), or None to clear
        #   'bold' - True or False for whether the text is bold
        #   'underline' - True or False for whether the text is underlined
        self.styling_colours = {
                '.header.cause': {'fg': 'red'},
                '.header.context': {'fg': 'red'},
                '.header.traceback': {'fg': 'red'},
                '.header.frame-repeated': {'bold': None},
                '.header.file': {'bold': None},
                '.header.file.filename': {'fg': 'yellow'},
                '.header.file.function-name': {'fg': 'yellow'},
                '.varname': {'fg': 'cyan'},
                '.line-exception': {'fg': 'magenta'},
                #'.line-exception.line-divider': {'bg': 'red', 'fg': 'black'},
                '.internal-exception': {'fg': 'red'},
                '.exception-name': {'fg': 'red'},
                '.exception-message': {'fg': 'red'},
            }

    def default_filter_frames(self, frames):  # pylint: disable=no-self-use
        """
        Call the default extensions to filter frames, unless filtering has been
        globally disabled (not currently implemented)
        """
        import longtraceback.Extensions
        return longtraceback.Extensions.frames_filter(frames)

    @classmethod
    def parameters(cls):
        """
        Return a list of the parameters, and the comments that go with them.
        """
        if cls._parameters:
            return cls._parameters

        init_text = inspect.getsource(cls.__init__)
        init_fh = IOClass.StringIO(init_text)

        def trim_comment(comment):
            if not comment:
                return ''

            if comment[0:2] == '# ':
                comment = comment[2:]
            if comment == '#':
                comment = ''

            return comment

        params = []
        last = tokenize.NEWLINE
        inside = 'start'
        param = {}
        # pylint: disable=unused-variable
        for toktype, tok, start, end, line in tokenize.generate_tokens(init_fh.readline):

            # For debugging:
            #print("token: %s(%s) : %r : %s" % (toktype, token.tok_name[toktype], tok, inside))

            if toktype in (tokenize.NEWLINE, tokenize.NL) and \
               last in (tokenize.NEWLINE, tokenize.NL):
                inside = 'start'

            elif toktype == tokenize.COMMENT and \
                 inside == 'start':
                # New comment block started.
                inside = 'comment'
                param = {
                        'description': [],
                        'variables': [],
                        'type': 'unknown',
                        'in-config': False
                    }
                params.append(param)
                if tok != '##':
                    param['description'].append(trim_comment(tok))

            elif toktype == tokenize.NL and \
                 inside == 'comment':
                # End of a comment line. Just ignore.
                pass

            elif toktype == tokenize.COMMENT and \
                 inside == 'comment':
                # Continuing a comment
                param['description'].append(trim_comment(tok))

            elif toktype == tokenize.NAME and \
                 last in (tokenize.NEWLINE, tokenize.NL) and \
                 inside in ('comment', 'nextvariable') and \
                 tok == 'self':
                # Start of a variable name
                inside = 'variable'

            elif toktype == tokenize.OP and \
                 tok == '.' and \
                 inside == 'variable':
                # That's fine, we're moving on to the variable name
                pass

            elif toktype == tokenize.NAME and \
                 inside == 'variable':
                # And now we're in a variable name
                name = tok
                param['variables'].append(name)

                default = getattr(defaults, name)
                if isinstance(default, str):
                    param['type'] = 'string'
                elif isinstance(default, bool):
                    param['type'] = 'boolean'
                elif isinstance(default, list):
                    param['type'] = 'list'
                elif isinstance(default, int):
                    param['type'] = 'number'
                elif isinstance(default, dict):
                    param['type'] = 'mapping'
                elif isinstance(default, types.FunctionType):
                    param['type'] = 'function'
                else:
                    param['type'] = 'unknown'

                if param['type'] in ('string', 'boolean', 'number'):
                    param['in-config'] = True

            elif toktype == tokenize.OP and \
                 tok == '=' and \
                 inside == 'variable':
                # Moved on to an assignment
                inside = 'assignment'

            elif inside == 'assignment':
                # Ignore everything inside the assignment, except the newline
                if toktype == tokenize.NEWLINE:
                    inside = 'nextvariable'

            else:
                inside = 'unknown'

            last = toktype

        cls._parameters = params
        return params

    @staticmethod
    def escape_config(s):
        s = str(s)
        s = s.replace('\\', '\\\\')
        s = s.replace('\n', '\\n')
        s = s.replace('\t', '\\t')
        return s

    @staticmethod
    def unescape_config(s):
        s = s.replace('\\\\', '\\')
        s = s.replace('\\n', '\n')
        s = s.replace('\\t', '\t')
        return s

    def read_user_config_file(self):
        config_file = os.environ.get('PYTHONLONGTRACEBACKCONFIG', None)
        if not config_file:
            config_file = os.path.expanduser('~/.python.longtraceback')
        self.read_config_file(config_file)

    def read_config_file(self, config_file):
        with open(config_file, 'r') as fh:
            self.read_config(fh)

    def read_config(self, fh):
        config = configparser.RawConfigParser()
        config.readfp(fh)

        self._settings_from_config = []
        if config.has_section('options'):
            # Override options for the configuration

            for key in config.options('options'):
                if not hasattr(self, key):
                    print("Option '%s' in configuration is not understood" % (key,))
                    continue

                # The default values also implicitly define the type of value
                # that we will use.
                current_value = getattr(self, key)
                if isinstance(current_value, bool):
                    value = config.getboolean('options', key)
                elif isinstance(current_value, int):
                    value = config.getint('options', key)
                elif isinstance(current_value, str):
                    value = self.unescape_config(config.get('options', key))
                else:
                    print("Option '%s' in configuration cannot be initialised" % (key,))
                    continue

                setattr(self, key, value)
                self._settings_from_config.append(key)

        self._colour_from_config = False
        if config.has_section('style'):
            # The 'styling_colours' initialisation
            self._colour_from_config = True

            styling_colours = {}
            for key, value in config.items('style'):
                properties = [x.strip() for x in value.split(',')]
                property_dict = {}
                for prop in properties:
                    if '=' in prop:
                        n, v = prop.split('=')
                        property_dict[n] = v
                    else:
                        property_dict[prop] = None
                styling_colours[key] = property_dict

            self.styling_colours = styling_colours

        # Clear the setup so that we use the updated settings
        import longtraceback
        longtraceback.Styling.styling_setup = None
        _ = longtraceback.Styling.StyledString('dummy')

    def write_config_file(self, config_file, unused='commented'):
        """
        Write a configuration file.

        The configuration that has been set in the loaded configuration file is remembered,
        and can be written out:

            - without any of the unused options (unused = 'hidden')
            - with any unused options commented out (unused = 'commented')
            - with the unused options included with the default settings (unused = 'default')
        """
        with open(config_file, 'w') as fh:
            self.write_config(fh, unused)

    def write_config(self, fh=None, unused='commented'):
        """
        Write a configuration file to a file handle.

        The configuration that has been set in the loaded configuration file is remembered,
        and can be written out:

            - without any of the unused options (unused = 'hidden')
            - with any unused options commented out (unused = 'commented')
            - with the unused options included with the default settings (unused = 'default')
        """
        if fh is None:
            fh = sys.stdout

        fh.write('[options]\n')
        for param in self.parameters():
            if not param['in-config']:
                continue

            if any(var in self._settings_from_config for var in param['variables']) or \
               any(getattr(self, var) != getattr(defaults, var) for var in param['variables']) or \
               unused != 'hidden':
                # either var changed or was in config file on load, or we include anyhow
                fh.write('\n')
                for line in param['description']:
                    fh.write('# %s\n' % (line,))

                for var in param['variables']:
                    var_updated = var in self._settings_from_config or \
                                  getattr(self, var) != getattr(defaults, var)

                    if not var_updated and unused == 'hidden':
                        # This variable should be hidden because it's not changed
                        continue
                    if unused == 'commented' and not var_updated:
                        # This variable should be commented out because it's not changed
                        fh.write('#')
                    fh.write('%s = %s\n' % (var, self.escape_config(getattr(self, var))))

        if self._colour_from_config or \
           self.styling_colours != defaults.styling_colours or \
           unused != 'hidden':
            commented = unused == 'commented' and \
                        not (self._colour_from_config or \
                             self.styling_colours != defaults.styling_colours)

            fh.write('\n\n%s[style]\n' % ('#' if commented else '',))

            for rule, props in sorted(self.styling_colours.items()):

                prop_list = []
                for prop, value in sorted(props.items()):
                    if value is None:
                        prop_list.append(prop)
                    else:
                        prop_list.append('%s=%s' % (prop, value))
                if commented:
                    fh.write('#')
                fh.write('%s = %s\n' % (rule, ', '.join(prop_list)))


# Ensure we have a set of defaults defined.
defaults = LongTracebackOptions()


if __name__ == '__main__':
    import argparse
    usage = "python -mlongtraceback.Options"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('--defaults', dest="unused",
                        action='store_const', const='defaults',
                        help="Include the default values (do not comment them out)", default='commented')

    options = parser.parse_args()

    defaults.write_config(sys.stdout, unused=options.unused)
