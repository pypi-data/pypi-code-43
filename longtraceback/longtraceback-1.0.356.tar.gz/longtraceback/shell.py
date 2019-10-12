#!/usr/bin/env python
"""
Shell for running a program with the traceback present.

Much deep magic is involved here:

  - We execute the program requested within a new context.
  - Within the context the longtraceback is in use.
  - On the termination of the script, the shell (the code.InteractiveConsole) is invoked.
  - The shell is in the same context as the program.
  - Readline history is saved to ~/.pyhist.
  - Readline tab completions are enabled for the new context.
  - Readline supports search forward and backward in history on ctrl-s and ctrl-r.

After an exception has occurred, the following variables are available:

  - sys.fail_type        Class of the last exception
  - sys.fail_value       Exception object
  - sys.fail_traceback   Traceback objects (as the usual linked list)
  - sys.fail_stack       Traceback stack (as a list)

"""

from __future__ import print_function

import argparse
import code
import os
import sys
import types

from pkgutil import read_code

import longtraceback.SysUtils
import longtraceback.DisplayHook
import longtraceback.ExceptHook

if sys.version_info < (3, 3):
    # Prior to Python 3.3, 'imp' was safe to import and use NullImporter.
    import imp
    nullimporter = imp.NullImporter
else:
    # For Python 3.3 and higher, 'None' has the same semantics as the imp.NullImporter.
    nullimporter = None


def _get_code_from_file(fname):
    # Check for a compiled file first
    with open(fname, "rb") as f:
        pycode = read_code(f)
    if pycode is None:
        # That didn't work, so try it as normal source code
        mode = 'r'
        if sys.version_info.major == 2:
            mode = 'rU'
        with open(fname, mode) as f:
            pycode = compile(f.read(), fname, 'exec', dont_inherit=True)
    return pycode


class InteractiveConsoleException(Exception):
    pass


class ConsoleCommandReplacement(object):
    def match(self, line):
        if line.startswith('s/'):
            return self.replacement

        return None

    def replacement(self, line):  # pylint: disable=R0201
        """
        Apply a replacement to the source file with the last exception.

        Global replacement is only supported in the flags; none of the other flags are supported.
        """
        import re
        import shutil

        delimiter = line[1]
        line = line[2:]
        globally = False
        if line.endswith('g'):
            line = line[:-1]
            globally = True

        if not line.endswith(delimiter):
            raise InteractiveConsoleException("No terminating delimiter found on replacement regex")

        line = line[:-1]

        match = re.search(r'^((?:[^\\]*(?:\\.)*)*)' + delimiter + r'((?:[^\\]*(?:\\.)*)*)$', line)
        if not match:
            raise InteractiveConsoleException("Could not determine replacement regex")

        replace_from = match.group(1)
        replace_to = match.group(2)

        if not sys.fail_stack:
            raise InteractiveConsoleException("No traceback present")

        # Last exception file
        last_filename = sys.fail_stack[-1].tb_frame.f_code.co_filename
        last_lineno = sys.fail_stack[-1].tb_lineno

        try:
            with open(last_filename, 'rU') as fh:
                content = fh.readlines()
        except IOError as ex:
            raise InteractiveConsoleException("Cannot read '%s': %s" % (last_filename, ex.strerror))

        # Perform the replacement
        count = 1
        if globally:
            count = 0
        newline, replacements = re.subn(replace_from, replace_to, content[last_lineno - 1], count=count)
        if replacements == 0:
            raise InteractiveConsoleException("No replacements performed")

        # Replace the line
        content[last_lineno - 1] = newline

        # Copy the file, in case we happen to destroy it (which we hope we won't)
        shutil.copyfile(last_filename, '%s.bak' % (last_filename,))
        with open(last_filename, 'w') as fh:
            fh.writelines(content)
        print("Replaced '%s' with '%s' in '%s'" % (replace_from, replace_to, last_filename))


class SpecialInteractiveConsole(code.InteractiveConsole):
    """
    Special console which allows us to run some special commands that we provide, but
    which are not within the environment. It also allows us to track the exceptions
    that have been encountered.
    """
    def __init__(self, *args, **kwargs):
        import sys  # pylint: disable=W0621,W0404
        try:
            sys.exc_clear()
        except:  # pylint: disable=bare-except
            pass
        sys.fail_type = None
        sys.fail_value = None
        sys.fail_traceback = None
        sys.fail_stack = []

        code.InteractiveConsole.__init__(self, *args, **kwargs)

        self.extensions = []
        self.extensions.append(ConsoleCommandReplacement())

    @staticmethod
    def is_commandline(filename):
        return filename.startswith('<') and filename.endswith('>')

    def _record_traceback(self):  # pylint: disable=no-self-use
        """
        Remember the frame we're in so that we can operate on the failures within the
        environment.
        """
        exc_class, exc, trace = sys.exc_info()

        if trace.tb_next is not None:
            # Skip the frame for our code
            trace = trace.tb_next

            filename = trace.tb_frame.f_code.co_filename

            # We only remember exceptions which were not caused by the console. Simple heuristic.
            # We take a copy of the traceback stack as a list, as that's a lot easier
            # to process and it ensures that subsequent operations don't break our
            # list (as would happen if any other exception happened, because the chain
            # would no longer be valid).
            if not self.is_commandline(filename):
                sys.fail_type = exc_class
                sys.fail_value = exc
                sys.fail_traceback = trace
                sys.fail_stack = []
                while trace:
                    sys.fail_stack.append(trace)
                    trace = trace.tb_next

    def showtraceback(self):
        """
        Augment the traceback by remembering the stack.

        We may not wish to do this at the interactive console, as it will replace the actual
        failing code's traceback.
        """
        try:
            self._record_traceback()

            code.InteractiveConsole.showtraceback(self)
        except Exception as ex:  # pylint: disable=broad-except
            print("Failure during 'showtraceback': %r" % (ex,))

            # Use the original traceback functions to see the traceback.
            import longtraceback  # pylint: disable=redefined-outer-name
            _, _, tb = sys.exc_info()
            for line in longtraceback.traceback_format_list(longtraceback.traceback_extract_tb(tb)):
                for subline in line.splitlines():
                    print("    %s" % (subline,))

    def showsyntaxerror(self, *args, **kwargs):
        """
        Augment the traceback by remembering the stack.

        We may not wish to do this at the interactive console, as it will replace the actual
        failing code's traceback.
        """
        self._record_traceback()

        code.InteractiveConsole.showsyntaxerror(self, *args, **kwargs)

    def runsource(self, source, filename='<input>', symbol='single'):
        """
        Intercept the commands we want to provide.
        """
        import traceback

        # Usually regex's can be delimited by anything. I'm being lazy.
        func = None
        for ext in self.extensions:
            func = ext.match(source)
            if func is not None:
                break
        if func:
            try:
                func(source)
                return False

            except InteractiveConsoleException as ex:
                for line in traceback.format_exception_only(type(ex), ex):
                    print(line.rstrip())
                return False

            except (Exception, KeyboardInterrupt):  # pylint: disable=W0703
                self.showtraceback()
                # Returning the string None makes the command execute, return None, which is then not
                # displayed by the shell.
                return False

        # Old style classes cannot use super - we must call the parent directly.
        with longtraceback.DisplayHook.PPDisplayHook(), \
             longtraceback.ExceptHook.StdoutExceptHook():
            return code.InteractiveConsole.runsource(self, source, filename, symbol)

    def write(self, message):
        # Note: The following may be useful for debugging:
        #message = repr(message) + '\n\n'
        sys.stdout.write(str(message))


def configure_longtraceback(options):  # pylint: disable=unused-argument,redefined-outer-name
    """
    Long traceback configuration.
    """

    try:
        import longtraceback  # pylint: disable=redefined-outer-name
        old_filter_frames = longtraceback.options.filter_frames

        def shell_filter_frames(frames):
            # If there are any frames for the console, or for this script, remove up to that point.
            this_file = configure_longtraceback.__code__.co_filename  # pylint: disable=no-member
            hidden_names = [this_file, code.__file__]
            if 'codeop' in sys.modules:
                hidden_names.append(sys.modules['codeop'].__file__)
            console_names = ('<stdin>', '<console>')

            # If there is a console in the stack trace, list only after that.
            new_list = []
            for frame in frames:
                filename = frame.tb_frame.f_code.co_filename
                if new_list or filename in console_names:
                    new_list.append(frame)
            if len(new_list) > 0:
                frames = new_list

            # If there is our 'execute_code' function in the trace, remove up to that point.
            new_list = []
            for frame in frames:
                filename = frame.tb_frame.f_code.co_filename
                if new_list or (filename == this_file and frame.tb_frame.f_code.co_name == 'execute_code'):
                    new_list.append(frame)
            if len(new_list) > 0:
                frames = new_list

            # Now trim off any of the hidden frames
            new_list = []
            for frame in frames:
                filename = frame.tb_frame.f_code.co_filename
                if filename not in hidden_names:
                    new_list.append(frame)

            frames = old_filter_frames(new_list)

            return frames

        longtraceback.options.filter_frames = shell_filter_frames
    except Exception as ex:
        raise ImportError("Cannot import 'longtraceback' for the shell: %r" % (ex,))


class InteractiveReadline(object):
    """
    Manage the ReadLine handling, outside of the interactive console.
    """

    def __init__(self):
        self.enabled = False
        self.have_readline = None
        self.loaded = False
        self.history_file = os.path.join(os.path.expanduser("~"), ".pyhist")
        self.readline = None
        self.rlcompleter = None

    @property
    def is_libedit(self):
        if self.readline:
            return 'libedit' in (getattr(self.readline, '__doc__', '') or '')

        return False

    def __repr__(self):
        if not self.loaded:
            state = "not loaded"
        elif self.have_readline:
            state = "available"
        else:
            state = "unavailable"

        if state != "available":
            return "InteractiveReadline(%s)" % (state,)

        enabled = "disabled"
        if self.enabled:
            enabled = "enabled"
        implementation = "readline"
        if self.is_libedit:
            implementation = "libedit"

        return "InteractiveReadline(%s, %s, %s)" % (state, implementation, enabled)

    def load(self):
        if self.loaded:
            return

        self.have_readline = True
        try:
            import readline
            import rlcompleter

            self.readline = readline
            self.rlcompleter = rlcompleter

            # Set up the readline system
            if self.is_libedit:
                # Under OS X, Apple avoided incorporating a GNU Readline, and instead use a BSD
                # 'libedit'. This has slightly different syntax for its configuration files,
                # so we try to use its format first. We still try the GNU format, in case someone
                # has recompiled Python for OS X.
                readline.parse_and_bind("bind ^I rl_complete")
                readline.parse_and_bind("bind ^S em-inc-search-next")
                readline.parse_and_bind("bind ^R em-inc-search-prev")
            else:
                readline.parse_and_bind("tab: complete")

            try:
                readline.read_init_file()
            except (OSError, IOError):
                pass

            try:
                readline.read_history_file(self.history_file)
            except IOError:
                pass

        except ImportError:
            self.have_readline = False

        self.loaded = True

    def start(self, var_context=None):
        if self.enabled:
            # Already enabled, so keep that way.
            return

        self.load()

        if not self.have_readline:
            return

        var_context = var_context or globals()
        self.readline.set_completer(self.rlcompleter.Completer(var_context).complete)
        self.enabled = True

    def stop(self):
        if not self.enabled:
            return

        if self.have_readline:
            self.readline.write_history_file(self.history_file)

        self.enabled = False


def run_python_startup(iconsole):
    startup_file = os.environ.get('PYTHONSTARTUP', None)
    if not startup_file:
        return

    try:
        code_to_run = _get_code_from_file(startup_file)
        iconsole.runcode(code_to_run)
    except Exception:
        raise


def run_interactive_hook(iconsole):  # pylint: disable=unused-argument
    hook = getattr(sys, '__interactivehook__', None)
    if not hook:
        return

    hook()


def execute_code(filename, code_to_run, args=None, interactive='always'):

    new_main = types.ModuleType('__main__')
    if filename:
        new_argv = [filename] + args
    else:
        new_argv = ['']

    with longtraceback.SysUtils.SysModuleReplacement('__main__', new_main), \
            longtraceback.SysUtils.SysArgvReplacement(new_argv):
        our_globals = sys.modules['__main__'].__dict__

        our_globals.update({
            '__name__': '__main__',
            '__file__': filename or '<stdin>',
            '__loader__': nullimporter,
            '__package__': None,

            # Implicit import by filename, allowing the shell to live somewhere not on the path
            # FIXME This isn't necessarily the correct module name.
            'longtraceback': sys.modules['longtraceback']
        })

        # Ensure that the file we're running has the directory in the path
        if filename:
            dirname = os.path.abspath(os.path.dirname(filename))
        else:
            dirname = os.path.abspath('.')
        if dirname not in sys.path:
            sys.path.insert(0, dirname)
        sys.path = [path for path in sys.path if path]

        iconsole = SpecialInteractiveConsole(our_globals)
        did_fail = False
        did_exception = False
        if code_to_run:
            try:
                iconsole.runcode(code_to_run)
            except SystemExit as exc:
                if interactive == 'always':
                    iconsole.showtraceback()
                elif interactive == 'on-fail':
                    did_fail = exc.code != 0
                    if did_fail:
                        iconsole.showtraceback()
                else:
                    raise
            else:
                did_exception = sys.exc_info()[0] is not None

        if interactive == 'always' or \
           (interactive == 'on-fail' and did_fail) or \
           (interactive == 'on-exception' and did_exception):

            readline = InteractiveReadline()
            readline.start(our_globals)

            run_python_startup(iconsole)
            run_interactive_hook(iconsole)

            try:
                features = ['long traceback']
                warnings = []
                if readline.enabled:
                    features.append('line completion')
                else:
                    warnings.append('readline')
                if warnings:
                    warning_message = "; without %s" % (', '.join(warnings),)
                else:
                    warning_message = ''
                message = "\nPython %s (with %s%s)" % ('.'.join(str(x) for x in sys.version_info[0:3]),
                                                       ", ".join(features), warning_message)

                # Enter the interactive console, and don't print a message when we leave (a Python 3-ism)
                if sys.version_info.major == 3 and sys.version_info.minor >= 6:
                    iconsole.interact(message, exitmsg='')
                else:
                    iconsole.interact(message)
            finally:
                readline.stop()


if __name__ == '__main__':
    usage = "python -mlongtraceback.shell <options> [<scriptfile> [<args>...]]"
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-i', '--interactive', dest="interactive",
                        action='store_const', const='always',
                        help="Drop to interactive shell on execution completion", default='never')
    parser.add_argument('-F', '--interactive-on-fail',
                        dest="interactive", action='store_const', const='on-fail',
                        help="Drop to interactive shell on failure (non-0 exit code)")
    parser.add_argument('-I', '--interactive-on-exception',
                        dest="interactive", action='store_const', const='on-exception',
                        help="Drop to interactive shell on exception being raised (other than SystemExit)")
    parser.add_argument('script', default=None, nargs='?',
                        help="Python script to execute with the long traceback")
    parser.add_argument('args', nargs=argparse.REMAINDER,
                        help="Arguments to the script")

    (options, call_args) = parser.parse_known_args()

    configure_longtraceback(options)

    if options.script is None:
        mod_code = None
        options.interactive = 'always'
    else:
        try:
            mod_code = _get_code_from_file(options.script)
        except IOError as ex:
            print("%s: %s" % (type(ex).__name__, ex))
            sys.exit(1)

    execute_code(interactive=options.interactive, filename=options.script, args=options.args, code_to_run=mod_code)
    sys.exit(0)
