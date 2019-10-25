import unittest
from unittest import mock
import logging
import socket
import tempfile
import time, threading
import os, sys, io
from pyats import log
from pyats.log import cisco
import multiprocessing.util
import collections
from pyats.log.utils import banner
import subprocess, shutil, re

DATE_REGEX = '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}: '

class TestCiscoLogTags(unittest.TestCase):

    def test_tags_string(self):
        tags = cisco.CiscoLogTags(a=1,b=2)
        self.assertEqual(str(tags), '%[a=1][b=2]: ')

    def test_tags_empty(self):
        tags = cisco.CiscoLogTags()
        self.assertEqual(str(tags), '')

    def test_copy(self):
        self.assertEqual(type(cisco.CiscoLogTags().copy()),
                         cisco.CiscoLogTags)

class TestCiscoLogRecord(unittest.TestCase):

    def test_basic_record(self):
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        self.assertEqual(record.hostname, socket.gethostname())
        self.assertEqual(record.tags, {'pid': record.process,
                                    'pname':  record.processName})
        self.assertEqual(record.cisco_appname, name)
        self.assertEqual(record.cisco_sev, 6)
        self.assertEqual(record.cisco_msgname, 'INFO')
        self.assertNotIn('tid', record.tags)
        self.assertNotIn('tname', record.tags)

    def test_threading_tags(self):
        t1 = threading.Thread(target=time.sleep, args = (5,))
        t1.start()
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.tags['tid'], threading.get_ident())
        self.assertEqual(record.tags['tname'], threading.current_thread().name)

    def test_record_backwards_compatible(self):
        fmt = logging.Formatter(fmt = log.TaskLogFormatter.MESSAGE_FORMAT,
                              datefmt = log.ScreenFormatter.TIMESTAMP_FORMAT)
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        msg = fmt.format(record)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        regex = '\d+: %s: ' % socket.gethostname()
        regex += DATE_REGEX + '%%%s-6-INFO: ' % name
        regex += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), '')

        self.assertRegex(msg, regex)

    def test_record_backwards_compatible_multi_line(self):
        fmt = logging.Formatter(fmt = log.TaskLogFormatter.MESSAGE_FORMAT,
                                datefmt = log.ScreenFormatter.TIMESTAMP_FORMAT)
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='line1\nline2\nline3',
                                      exc_info=None)
        msg = fmt.format(record)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        regex = '\d+: %s: ' % socket.gethostname()
        regex += DATE_REGEX + '%%%s-6-INFO: ' % name
        regex += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), 'line1\nline2\nline3')

        self.assertRegex(msg, regex)

    def test_cisco_appname(self):

        record = cisco.CiscoLogRecord(name='cisco_shared.abc.d',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'ABC')

        record = cisco.CiscoLogRecord(name='regression.abc.d',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'ABC')

        record = cisco.CiscoLogRecord(name='xbu_shared.abc.d',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'ABC')

        record = cisco.CiscoLogRecord(name='pyats.awesome.is',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'AWESOME')

        record = cisco.CiscoLogRecord(name='pyats.log.tcl.mememe',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'TCL')

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='line1\nline2\nline3',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, name)

        record = cisco.CiscoLogRecord(name='pyats.aetest.testscript.myscript',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'SCRIPT')

        record = cisco.CiscoLogRecord(name='lalala',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg='',
                                      exc_info=None)
        self.assertEqual(record.cisco_appname, 'LALALA')

    def test_ciscosev(self):
        MAP = {
            'CRITICAL': 2,
            'ERROR': 3,
            'WARNING': 4,
            'INFO': 6,
            'DEBUG': 7,
        }

        for k, v in MAP.items():
            record = cisco.CiscoLogRecord(name='lalala',
                                          level=getattr(logging, k),
                                          lineno = 1,
                                          pathname = __file__,
                                          args = {},
                                          msg='',
                                          exc_info=None)
        self.assertEqual(record.cisco_sev, v)

class TestCiscoLogFormatter(unittest.TestCase):

    def setUp(self):
        cisco.LOG_SEQUENCE_COUNTER.clear()

    def tearDown(self):
        cisco.LOG_SEQUENCE_COUNTER.clear()

    def test_exception_output(self):
        fmt = cisco.CiscoLogFormatter(
                              fmt = log.TaskLogFormatter.MESSAGE_FORMAT,
                              datefmt = log.ScreenFormatter.TIMESTAMP_FORMAT)

        try:
            abcdef
        except:
            record = cisco.CiscoLogRecord(name=__name__,
                                          level=logging.INFO,
                                          lineno = 1,
                                          pathname = __file__,
                                          args = {},
                                          msg='Caught Exception',
                                          exc_info=sys.exc_info())
            record_formatted = fmt.format(record)

        expected = r'''Caught Exception
Traceback \(most recent call last\):
  File "%s", line \d+, in test_exception_output
    abcdef
NameError: name 'abcdef' is not defined''' % __file__

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        for index, (line, expectation) in \
                enumerate(zip(record_formatted.splitlines(),
                              expected.splitlines()), 0):
            fmt = '%s: %s: ' % (index, socket.gethostname())
            fmt += DATE_REGEX + '%%%s-6-INFO: ' % name
            fmt += '%%\[part=0\.%s\/5\]\[pid=%s\]\[pname=MainProcess\]: %s' % \
                   (index+1, os.getpid(), expectation)
            self.assertRegex(line, fmt)

    def test_multi_line(self):
        fmt = cisco.CiscoLogFormatter(
                              fmt = log.TaskLogFormatter.MESSAGE_FORMAT,
                              datefmt = log.ScreenFormatter.TIMESTAMP_FORMAT)

        msg = '''this
is
a
multiline
msg'''
        record = cisco.CiscoLogRecord(name=__name__,
                                    level=logging.INFO,
                                    lineno = 1,
                                    pathname = __file__,
                                    args = {},
                                    msg=msg,
                                    exc_info=None)
        record_formatted = fmt.format(record)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        for index, (line, expectation) in \
                enumerate(zip(record_formatted.splitlines(),
                              msg.splitlines()), 0):
            fmt = '%s: %s: ' % (index, socket.gethostname())
            fmt += DATE_REGEX + '%%%s-6-INFO: ' % name
            fmt += '%%\[part=0\.%s\/5\]\[pid=%s\]\[pname=MainProcess\]: %s' % \
                   (index+1, os.getpid(), expectation)
            self.assertRegex(line, fmt)


class Test_TaskLogHandler(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger('Test_ColouringFunctings')
        self.logger.handlers.clear()
        self.logger.propagate = False
        self.stream = io.StringIO()
        f = tempfile.NamedTemporaryFile().name
        self.handler = log.TaskLogHandler(f, coloured = True)
        self.handler.stream = self.stream
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def test_colour(self):
        self.logger.info('abc', extra = {'colour': 'magenta'})

        output = self.handler.stream.getvalue()
        self.assertTrue(']: \033[35m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_bold(self):
        self.logger.info('abc', extra = {'colour': 'blue',
                                         'style': 'bold'})

        output = self.handler.stream.getvalue()
        print(repr(output))
        self.assertTrue(']: \033[34m\033[1m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_light(self):
        self.logger.info('abc', extra = {'colour': 'blue',
                                         'style': 'light'})

        output = self.handler.stream.getvalue()
        self.assertTrue(']: \033[34m\033[2m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))


class Test_ScreenHandler(unittest.TestCase):

    def setUp(self):
        self.logger = logging.getLogger('Test_ColouringFunctings')
        self.logger.handlers.clear()
        self.logger.propagate = False
        self.stream = io.StringIO()
        self.handler = log.ScreenHandler(stream = self.stream)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)

    def test_info(self):
        self.logger.info('abc')
        self.assertTrue(self.handler.stream.getvalue().endswith('abc\n'))

    def test_error(self):
        self.logger.error('abc')
        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-ERROR: \033[31m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_debug(self):
        self.logger.debug('abc')
        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-DEBUG: \033[36m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_warning(self):
        self.logger.warning('abc')
        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-WARNING: \033[33m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_critical(self):
        self.logger.critical('abc')
        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-CRITICAL: '
                        '\033[1m\033[31m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))


    def test_colour(self):
        self.logger.info('abc', extra = {'colour': 'magenta'})

        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-INFO: \033[35m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_bold(self):
        self.logger.info('abc', extra = {'colour': 'blue',
                                         'style': 'bold'})

        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-INFO: \033[34m\033[1m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_light(self):
        self.logger.info('abc', extra = {'colour': 'blue',
                                         'style': 'light'})

        output = self.handler.stream.getvalue()
        self.assertTrue('%TEST_COLOURINGFUNCTINGS-INFO: '
                        '\033[34m\033[2m' in output)
        self.assertTrue(output.endswith('abc\033[0m\033[39m\n'))

    def test_format_exception(self):
        try:
            raise Exception('asdfsadf')
        except Exception:
            self.logger.exception('caught exception')

        output = self.handler.stream.getvalue()
        self.assertIn('\x1b[31mcaught exception\x1b[0m\x1b[39m\n', output)
        self.assertIn('\x1b[31mTraceback (most recent call last):\x1b[0m\x1b[39m\n', output)

@unittest.skipIf(os.geteuid() == 0, 'skip for root user')
class TestAtslogFunctions(unittest.TestCase):

    def setUp(self):
        cisco.LOG_SEQUENCE_COUNTER.clear()
        self.temp = tempfile.NamedTemporaryFile()

    def tearDown(self):
        cisco.LOG_SEQUENCE_COUNTER.clear()

        multiprocessing.util._afterfork_registry.clear()

    def test_global_handlers(self):
        self.assertTrue(isinstance(log.managed_handlers.tasklog,
                                   log.TaskLogHandler))
        self.assertTrue(isinstance(log.managed_handlers.screen,
                                   log.ScreenHandler))
        self.assertEqual(log.managed_handlers.tasklog.stream.name, os.devnull)
        self.assertEqual(log.managed_handlers.screen.stream, sys.stdout)

    def test_formatters_are_there(self):
        self.assertTrue(issubclass(log.ScreenFormatter, logging.Formatter))
        self.assertTrue(issubclass(log.TaskLogFormatter,
                                   log.ScreenFormatter))

    def test_sys_stdout_tracking(self):
        handler = log.ScreenHandler()
        self.assertTrue(handler.stream is sys.stdout)
        try:
            bkup = sys.stdout
            sys.stdout = object()
            self.assertTrue(handler.stream is sys.stdout)
        finally:
            sys.stdout = bkup

    def test_custom_stream(self):
        stream = object()
        handler = log.ScreenHandler(stream)
        self.assertTrue(handler.stream is stream)
        self.assertTrue(handler.stream is stream) # check x2

    def test_screen_format(self):
        formatter = log.ScreenFormatter()

        msg = "test message"
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        fmt = DATE_REGEX + '%%%s-INFO: %s' %  (name, msg)

        self.assertRegex(record_formatted, fmt)

    def test_screen_format_multi_line(self):

        formatter = log.ScreenFormatter()

        msg = "test\nmessage"
        record = cisco.CiscoLogRecord(name=__name__,
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        if __name__ == '__main__':
            name = 'SCRIPT'
        else:
            if '.' in __name__:
                name = __name__.split('.')[1].upper()
            else:
                name = __name__.upper()

        for i,j in zip(msg.splitlines(), record_formatted.splitlines()):
            fmt = DATE_REGEX + '%%%s-INFO: %s' %  (name, i)
            self.assertRegex(j, fmt)

    def test_screen_handler(self):

        handler = log.ScreenHandler()

        self.assertTrue(isinstance(handler.formatter, log.ScreenFormatter))
        self.assertTrue(handler.coloured)
        self.assertIs(handler.stream, sys.stdout)

        self.assertIs(log.ScreenHandler(sys.stderr).stream, sys.stderr)
        self.assertIs(log.ScreenHandler(coloured=False).coloured, False)

        self.assertIs(type(handler.formatter), log.ColouredScreenFormatter)
        self.assertIs(type(log.ScreenHandler(coloured=False).formatter),
                      log.ScreenFormatter)
        # shouldn't need to test anything else
        # stdout is stdout, formatter is set, nothing we need to do.

    def test_trim_module_name(self):
        formatter = log.ScreenFormatter()
        msg = "test message"
        record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        fmt = DATE_REGEX + '%%MIDDLE-INFO: %s' %  msg

        self.assertRegex(record_formatted, fmt)

    def test_tasklog_format(self):
        formatter = log.TaskLogFormatter()

        msg = "test message"
        record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        hostname = hostname = socket.gethostname()

        fmt = '\d+: %s: ' % hostname
        fmt += DATE_REGEX + '%MIDDLE-6-INFO: '
        fmt += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), msg)

        self.assertRegex(record_formatted, fmt)

    def test_log_tcl_formatting(self):
        formatter = log.TaskLogFormatter()

        msg = "test message"
        record = cisco.CiscoLogRecord(name='pyats.log.tcl.caas',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        hostname = hostname = socket.gethostname()

        fmt = '\d+: %s: ' % hostname
        fmt += DATE_REGEX + '%TCL-6-CAAS: '
        fmt += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), msg)

        self.assertRegex(record_formatted, fmt)

    def test_seqnum(self):
        from collections import Counter

        # reset the counter
        log.TaskLogFormatter.thread_seqnum = Counter()

        formatter = log.TaskLogFormatter()
        msg = "test message"
        record = cisco.CiscoLogRecord(name='pyats.log.tcl.caas',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        hostname = hostname = socket.gethostname()

        fmt = '0: %s: ' % hostname
        fmt += DATE_REGEX + '%TCL-6-CAAS: '
        fmt += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), msg)

        self.assertRegex(record_formatted, fmt)

        record = cisco.CiscoLogRecord(name='pyats.log.tcl.caas',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        fmt = '1: %s: ' % hostname
        fmt += DATE_REGEX + '%TCL-6-CAAS: '
        fmt += '%%\[pid=%s\]\[pname=MainProcess\]: %s' % \
               (os.getpid(), msg)

        self.assertRegex(record_formatted, fmt)

        from pyats.log.utils import banner

        msg = banner('lalala\nlala')

        record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        for i, line in enumerate(record_formatted.splitlines(), 2):
            fmt = '%s: %s: ' % (i,hostname)
            fmt += DATE_REGEX + '%MIDDLE-6-INFO: '
            self.assertRegex(line, fmt)

    def test_tasklog_format_multi_line(self):
        formatter = log.TaskLogFormatter()

        msg = "test\nmessage"
        record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)

        record_formatted = formatter.format(record)

        hostname = socket.gethostname()
        self.assertEqual(len(record_formatted.splitlines()), 2)

        for index, line in enumerate(record_formatted.splitlines(), 1):
            fmt = '%s: %s: ' % (index-1,hostname)
            fmt += DATE_REGEX + '%MIDDLE-6-INFO: '
            fmt += '%%\[part=0\.%s\/2\]\[pid=%s\]\[pname=MainProcess\]: %s' % \
                   (index, os.getpid(), msg.splitlines()[index-1])
            self.assertRegex(line, fmt)


        msg = 'a\nb\nc\r\nd'

        record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                      level=logging.INFO,
                                      lineno = 1,
                                      pathname = __file__,
                                      args = {},
                                      msg=msg,
                                      exc_info=None)
        record_formatted = formatter.format(record)

        self.assertEqual(len(record_formatted.splitlines()), 4)

        for index, line in enumerate(record_formatted.splitlines(), 1):
            fmt = '%s: %s: ' % (index+1,hostname)
            fmt += DATE_REGEX + '%MIDDLE-6-INFO: '
            fmt += '%%\[part=2\.%s\/4\]\[pid=%s\]\[pname=MainProcess\]: %s' % \
                   (index, os.getpid(), msg.splitlines()[index-1])
            self.assertRegex(line, fmt)


    def test_tasklog_format_legacy_levels(self):
        formatter = log.TaskLogFormatter()

        for i, j in zip([6,7,4,3,2],['INFO',
                                     'DEBUG',
                                     'WARNING',
                                     'ERROR',
                                     'CRITICAL' ]):

            record = cisco.CiscoLogRecord(name='pyats.middle.end',
                                          level=getattr(logging, j),
                                          lineno = 1,
                                          pathname = __file__,
                                          args = {},
                                          msg='',
                                          exc_info=None)
            fmt = '%%MIDDLE-%s-%s' % (i,j)
            self.assertRegex(formatter.format(record), fmt)

    def test_tasklog_handler(self):

        self.assertTrue(issubclass(log.TaskLogHandler,
                                   logging.StreamHandler))

        self.assertTrue(hasattr(log.TaskLogHandler, 'changeFile'))

        handler = log.TaskLogHandler(self.temp.name)

        self.assertTrue(isinstance(handler.formatter, log.TaskLogFormatter))

        logger = logging.getLogger('test')
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)

        logger.info('test msg 1')
        logger.info('test msg with\nlinebreak')

        handler.close()

        self.assertIs(handler.stream, None)

        self.assertNotIn(handler.get_name(), logging._handlers)

        with open(self.temp.name, 'r') as f:
            data = f.read()

        self.assertTrue(data)

        self.assertRegex(data, 'test msg 1')
        self.assertRegex(data, 'test msg with')
        self.assertRegex(data, 'linebreak')

    def test_change_handler(self):

        handler = log.TaskLogHandler(self.temp.name)

        self.assertIn(handler.get_name(), logging._handlers)
        self.assertEqual(handler.get_name(), 'TaskLog-%s' % self.temp.name)

        self.assertEqual(handler.stream.name, self.temp.name)

        # change to new file
        try:
            new_file = os.path.join(os.path.dirname(self.temp.name), 'other.tmp')

            # store stream to make sure it's cleaned
            stream = handler.stream
            handler.changeFile(new_file)

            self.assertTrue(stream.closed)
            self.assertEqual(handler.stream.name, new_file)
        finally:
            handler.close()
            os.remove(new_file)

    def test_handler_null(self):

        handler = log.TaskLogHandler('')
        self.assertEqual(handler.logdir, os.getcwd())
        self.assertEqual(handler.stream.name, os.devnull)
        self.assertEqual(handler.logfile, '')
        handler.close()

        handler = log.TaskLogHandler(None)
        self.assertEqual(handler.logdir, os.getcwd())
        self.assertEqual(handler.stream.name, os.devnull)
        self.assertEqual(handler.logfile, '')
        handler.close()

    def test_handler_dir(self):
        handler = log.TaskLogHandler(self.temp.name)
        self.assertEqual(handler.logdir, os.path.dirname(self.temp.name))

        try:
            new_file = os.path.join(os.path.dirname(self.temp.name), 'other.tmp')

            handler.changeFile('other.tmp')
            self.assertEqual(handler.stream.name, new_file)
            self.assertEqual(handler.logdir, os.path.dirname(self.temp.name))
        finally:
            handler.close()
            os.remove(new_file)

        handler = log.TaskLogHandler(self.temp.name)
        try:
            new_file = os.path.join(os.path.dirname(self.temp.name), 'other2.tmp')
            handler.changeFile('')
            self.assertEqual(handler.stream.name, os.devnull)
            self.assertEqual(handler.logdir, os.path.dirname(self.temp.name))
            handler.changeFile('other2.tmp')
            self.assertEqual(handler.stream.name, new_file)
            self.assertEqual(handler.logdir, os.path.dirname(self.temp.name))
        finally:
            handler.close()
            os.remove(new_file)

        try:
            handler = log.TaskLogHandler(None)
            pwd = os.getcwd()
            self.assertEqual(pwd, handler.logdir)
            new_file = os.path.join(os.path.join(pwd, 'other3.tmp'))
            handler.changeFile('other3.tmp')
            self.assertEqual(handler.stream.name, new_file)
        finally:
            handler.close()
            os.remove(new_file)

        handler = log.TaskLogHandler(self.temp.name)
        try:
            new_file = os.path.join(os.getcwd(), 'other4.tmp')
            handler.changeFile(new_file)
            self.assertEqual(handler.stream.name, new_file)
            self.assertEqual(handler.logdir, os.getcwd())
        finally:
            handler.close()
            os.remove(new_file)

    def test_enable_disable_forked(self):
        handler = log.TaskLogHandler(self.temp.name)

        import multiprocessing.util

        handler.enableForked()
        self.assertIn(handler,
                      multiprocessing.util._afterfork_registry.values())

        # do it twice - no errors
        handler.enableForked()
        self.assertIn(handler,
                      multiprocessing.util._afterfork_registry.values())


        handler.disableForked()
        self.assertNotIn(handler,
                         multiprocessing.util._afterfork_registry.values())

        # do it twice - no errors
        handler.disableForked()
        self.assertNotIn(handler,
                         multiprocessing.util._afterfork_registry.values())

    def test_forked_log(self):
        handler = log.TaskLogHandler(self.temp.name)

        handler.enableForked(consolidate = False)

        logging.root.addHandler(handler)

        import multiprocessing

        def dummy():
            logging.root.info('in child process')

        p = multiprocessing.Process(target=dummy)
        p.start()
        p.join()

        newlog = ':'.join([handler.logfile, 'pid-%s' % p.pid])
        self.assertTrue(os.path.isfile(newlog))

        p.terminate()

        os.remove(newlog)

        handler.disableForked()

    def test_forkRegistered(self):
        handler = log.TaskLogHandler(self.temp.name)
        self.assertFalse(handler.forkRegistered)
        handler.enableForked()
        self.assertTrue(handler.forkRegistered)
        handler.disableForked()
        self.assertFalse(handler.forkRegistered)

    def test_next_fork_logfile_no_enable(self):

        folder = tempfile.TemporaryDirectory()
        handler = log.TaskLogHandler(os.path.join(folder.name, 'a'))

        import multiprocessing

        def dummy():
            logging.root.info('in child process')
        self.assertFalse(os.path.isfile(os.path.join(folder.name, 'b')))
        with handler.next_fork_logfile('b', consolidate = False):
            p = multiprocessing.Process(target=dummy)
            p.start()
            p.join()

        self.assertTrue(os.path.isfile(os.path.join(folder.name, 'b')))

    def test_next_fork_logfile_enable(self):
        folder = tempfile.TemporaryDirectory()
        handler = log.TaskLogHandler(os.path.join(folder.name, 'a'))
        handler.enableForked(consolidate = False)
        import multiprocessing

        def dummy():
            logging.root.info('in child process')
        self.assertFalse(os.path.isfile(os.path.join(folder.name, 'b')))
        with handler.next_fork_logfile('b'):
            p = multiprocessing.Process(target=dummy)
            p.start()
            p.join()

        self.assertTrue(os.path.isfile(os.path.join(folder.name, 'b')))

    def test_fork_consolidate_logs(self):
        handler = log.TaskLogHandler(self.temp.name)

        handler.enableForked()

        logging.root.addHandler(handler)
        logging.root.setLevel(logging.INFO)
        logging.root.info('abc')

        import multiprocessing

        def dummy():
            logging.root.info('in child process')

        self.assertEqual(handler._consolidate_forked_logs, False)

        p = multiprocessing.Process(target=dummy)
        with handler.consolidate_next_forked_logfile():
            p.start()
        p.join()
        self.assertEqual(handler._consolidate_forked_logs, False)

        newlog = ':'.join([handler.logfile, 'pid-%s' % p.pid])

        p.terminate()

        handler.disableForked()
        handler.flush()

        expected = r'''0: .+?: .+?: %ROOT-6-INFO: %\[pid=\d+\]\[pname=MainProcess\]: abc
0: .+?: .+?: %LOG-6-INFO: %\[pid=\d+\]\[pname=Process-1\]: >>>> Begin child log .+
1: .+?: .+?: %ROOT-6-INFO: %\[pid=\d+\]\[pname=Process-1\]: in child process
2: .+?: .+?: %LOG-6-INFO: %\[pid=\d+\]\[pname=Process-1\]: <<<< End child log .+'''
        with open(handler.logfile) as f:
            data = f.read()

        for line, expected in zip(data.splitlines(), expected.splitlines()):
            self.assertRegex(line, expected)


@unittest.skipIf(os.geteuid() == 0, 'skip for root user')
class TestAtsLogScript(unittest.TestCase):

    def setUp(self):
        self.runinfo_dir = tempfile.mkdtemp(prefix='runinfo_dir')

    def tearDown(self):
        shutil.rmtree(self.runinfo_dir)

    def test_run_script(self):
        job = os.path.join(os.path.dirname(__file__), 'scripts', 'job.py')
        regex = os.path.join(os.path.dirname(__file__), 'scripts',
                'TaskLog_regex.txt')

        # Prevent pyats.conf files in $HOME/.pyats/ and $VIRTUAL_ENV/ from
        # being parsed
        environ = os.environ.copy()
        environ['HOME'] = self.runinfo_dir
        environ['VIRTUAL_ENV'] = self.runinfo_dir

        p = subprocess.Popen(['easypy', job,
                              '-runinfo_dir', self.runinfo_dir,
                              '-no_archive', '-no_mail'],
                              universal_newlines = True,
                              stdout = subprocess.PIPE,
                              env = environ)

        out, err = p.communicate()

        self.assertFalse(err)

        logdir = re.search('Logs can be found at: (.+)', out).groups()[0]

        with open(logdir+'/TaskLog.Task-1') as f:
            tasklog = f.read()

        tasklog = tasklog.splitlines()

        with open(regex) as f:
            expectation = f.read().splitlines()

        i = 3
        child = 0

        for line, expected in zip(tasklog, expectation):
            if 'ChildLabor' in expected:
                prefix = '%s: %s: ' % (child, socket.gethostname())
                child += 1
            else:
                prefix = '%s: %s: ' % (i, socket.gethostname())
                i += 1

            prefix += DATE_REGEX

            expected = expected % prefix

            self.assertRegex(line, expected)

        for finale in ("pyats.async_.exceptions.ChildProcessException: name 'aaa' "
                       "is not defined",
                       "The result of section pcall_exceptions is => ERRORED",
                       "The result of testcase Testcase is => ERRORED"):
            for line in tasklog:
                try:
                    self.assertRegex(line, finale)
                    break
                except AssertionError:
                    pass
            else:
                raise AssertionError("Missing %s" % finale)



if __name__ == '__main__': # pragma: no cover
    unittest.main()
