from __future__ import division, print_function, unicode_literals
import logging, sys, pdb, traceback, inspect, re, os, json, random, pstats
from logging import NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
from contextlib import contextmanager
from collections import namedtuple, deque
from datetime import datetime, timedelta
from math import sqrt
try:
    import cProfile as profile
except: #pragma: no cover
    import profile 

random.seed()

OFF = CRITICAL+10

is_py2 = sys.version_info[0] == 2
is_py3 = sys.version_info[0] == 3

if is_py2: #pragma: no cover
    from StringIO import StringIO
elif is_py3: #pragma: no cover
    from io import StringIO
__version__ = '1.0.0'

def parse_tlm(s,tlm_channel=None):
    """
    This function searches a string for telemetry log messages created by the logarhythm.tlm() function.
    All logged telemetry messages will be yielded as dictionaries mapping the original keyword arguments to their values.
    """
    if tlm_channel is not None:
        if '#' in tlm_channel:
            raise LogarhythmException('Cannot use the # character as part of the tlm_channel')
    for m in re.finditer('tlm_start_(?P<k>[0-9A-F]{8})\\((?P<content>.+?)\\)(?P=k)_tlm_end',s):
        content = m.group('content')
        msg_channel,json_content = re.search('(#[^#]+#){0,1}(.*)',content,re.S).groups()

        if tlm_channel is None or (msg_channel is not None and msg_channel[1:-1] == tlm_channel):
            yield json.loads(json_content)
        

def tlm(tlm_channel=None,**kwargs):
    """
    This function produces a log message string to be passed into a logger method that captures parameter names and values based on the provided keyword arguments.
    The keyword arguments and values are encoded into JSON messages. Only values that can be encoded in JSON are allowed.
    Logfiles that contain messages generated from this function can be parsed using the parse_tlm() function to extract these telemetry records.

    The first parameter, tlm_channel is a special optional parameter that will be attached to the logged message.
    The parse_tlm function can be configured to only include messages matching a specified tlm_channel value.

    >>> logger = Logger('doctest')
    >>> with logger.use(stdout=False,doctest_mode=True,level=INFO):
    ...    with logger.stream_open() as sh:
    ...       logger.info(tlm('channel A',x=5,y=10))
    ...       logger.info(tlm('channel A',x=9,y=11))
    ...       logger.info(tlm(z='trying to be tricky with )00000000_tlm_end inside the data itself'))
    ... 
    ... 
    >>> list(parse_tlm(sh.getvalue())) == [{'x':5,'y':10},{'x':9,'y':11},{'z':'trying to be tricky with )00000000_tlm_end inside the data itself'}]
    True
    >>> list(parse_tlm(sh.getvalue(),'channel A')) == [{'x':5,'y':10},{'x':9,'y':11}]
    True
    """
    if tlm_channel is not None:
        if '#' in tlm_channel:
            raise LogarhythmException('Cannot use the # character as part of the tlm_channel')
    
    content = json.dumps(kwargs)
    start_format = 'tlm_start_%s('
    end_format = ')%s_tlm_end'
    if tlm_channel is not None:
        start_format += ('#%s#'%tlm_channel)
        end_format += ('#%s#'%tlm_channel)
        
    k = '00000000'
    ending = end_format % k
    while ending in content:
        k = '%08X' % random.getrandbits(32)
        ending =  end_format % k
    return ''.join([(start_format%k),content,ending])

def _caller_name():
    caller_frame_info = inspect.stack()[2]
    name = caller_frame_info[0].f_globals['__name__']
    return name

def short_repr(x):
    """
    This is the same as repr() except it limits the string to 35 characters.
    If the string is more than 35 characters long, this will print the first 16 and the last 16 characters separated by an ellipsis "...".

    ```
    >>> short_repr(list(range(1000))) == '[0, 1, 2, 3, 4, ..., 997, 998, 999]'
    True

    ```
    """
    s = repr(x)
    if s.startswith("u'") or s.startswith('u"'):
        s = s[1:]
    if len(s) <= 35:
        return s
    else:
        return s[:16]+'...'+s[-16:]

class LogarhythmException(Exception): 
    """
    Base class for logarhythm specific Exceptions
    """
    pass

def build_format(time='hms',logger_name=True,process_name=False,thread_name=False,level=True):
    """
    This function tries to simplify generating logger formatting expressions, by determining the style and order.
    The user just needs to specify what information they want to include.

    Input valid values (first option listed is the default):
    
    - time = 'hms' | 'full' | 'elapsed_msec' | None
        - 'hms' = HH:MM:SS i.e. hour:minute:second within the current day
        - 'full' = yyyy-mm-dd/HH:MM:SS i.e. date + hour:minute:second
        - 'elapsed_msec' = Number of milliseconds elapsed since logging module was loaded
        - None =  Do not include time
    - logger_name = True | False
        - Whether to include the logger name
    - process_name = False | True
        - Whether to include the process name (for multiprocessing)
    - thread_name = False | True
        - Whether to include the thread name (for multithreading)
    - level = True | False
        - Whether to include the level of the message
    ```
    >>> import logarhythm
    >>> logger = logarhythm.getLogger()
    >>> logarhythm.build_format(time=None) == (u'[%(name)s :%(levelname)s] %(message)s', u'%H:%M:%S', u'%')
    True

    >>> build_format('full',False,True,True,False) == ('[%(asctime)s Process="%(processName)s" Thread="%(threadName)s"] %(message)s', '%Y-%m-%d/%H:%M:%S', '%')
    True
    >>> build_format('elapsed_msec') == ('[%(relativeCreated)s %(name)s :%(levelname)s] %(message)s', '%H:%M:%S', '%')
    True

    ```
    """
    format_pieces = []
    time_fmt = '%H:%M:%S'
    style = '%'
    if time == 'full':
        format_pieces.append('%(asctime)s')
        time_fmt = '%Y-%m-%d/%H:%M:%S'
    elif time == 'hms':
        format_pieces.append('%(asctime)s')
    elif time == 'elapsed_msec':
        format_pieces.append('%(relativeCreated)s')
    elif time is None:
        pass
    else:
        raise LogarhythmException('Invalid time input for build_format(): %s' % repr(time))
    if logger_name is True:
        format_pieces.append('%(name)s')
    elif logger_name is False:
        pass
    else:
        raise LogarhythmException('Invalid logger_name input for build_format(): %s' % repr(logger_name))
    if process_name is True:
        format_pieces.append('Process="%(processName)s"')
    elif process_name is False:
        pass
    else:
        raise LogarhythmException('Invalid process_name input for build_format(): %s' % repr(process_name))
    if thread_name is True:
        format_pieces.append('Thread="%(threadName)s"')
    elif thread_name is False:
        pass
    else:
        raise LogarhythmException('Invalid thread_name input for build_format(): %s' % repr(thread_name))
    if level is True:
        format_pieces.append(':%(levelname)s')
    elif level is False:
        pass
    else:
        raise LogarhythmException('Invalid level input for build_format(): %s' % repr(level))

    fmt = '[%s] %%(message)s' % ' '.join(format_pieces)
    return fmt, time_fmt, style


def capture_debug_callback(logger,caller_frame_info,match,level):
    """
    This is the default callback for the Logger.capture() method.
    This results in debug mode being entered when a logged message matches the captured pattern.
    """
    if not logger.debugging_disabled:
        pdb.Pdb().set_trace(caller_frame_info[0]) #pragma: no cover

def monitor_attr_debug_callback(logger,caller_frame_info,target,attr_name,old_value,new_value):#pragma: no cover
    """
    This is an optional callback that can be used with the Logger.monitor_attr() method.
    If utilized, then changes to the monitored attribute will result in debug mode being entered.
    """
    if not logger.debugging_disabled:
        pdb.Pdb().set_trace(caller_frame_info[0]) 

def monitor_call_debug_callback(logger,caller_frame_info,target_callable,args,kwargs):#pragma: no cover
    """
    This is an optional callback that can be used with the Logger.monitor_call() method.
    If utilized, then calling the monitored method will result in debug mode being entered.
    """
    if not logger.debugging_disabled:
        pdb.Pdb().set_trace(caller_frame_info[0])

def _auto_debug_handler(exc_type,exc_value,exc_traceback): # pragma: no cover
    traceback.print_exception(exc_type,exc_value,exc_traceback)
    print('Unhandled exception encountered and auto_debug is enabled.')
    pdb.post_mortem(exc_traceback)

def getLogger(name=None):
    """
    Returns the logarhythm logger with the given name

    ```
    >>> Logger() is getLogger()
    True
    >>> getLogger() is getLogger(__name__)
    True
    >>> Logger() is getLogger('.')
    True
    >>> Logger('.') is getLogger('.')
    True
    >>> Logger('.').child('doctest') is getLogger('.doctest')
    True
    
    ```
    """
    if name is None or name is '.':
        name = _caller_name()
    return Logger(name)

def getLogger_logging_module(name=None):
    """
        Returns a Logger as defined in the logging module but default name is \_\_name\_\_ instead of root
    """
    if name is None or name is '.':
        name = _caller_name()
    return original_getLogger(name)

def breakpoint(condition=True):#pragma: no cover
    """
    Same as getLogger().breakpoint(condition)
    """
    logger = getLogger()
    caller_frame_info = inspect.stack()[1]
    logger.breakpoint(condition,caller_frame_info)

def debug(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)
    
    See logging module for *args and **kwargs documentation.
    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    debug('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :DEBUG] test
    >>> logger.level
    0

    ```

    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.debug(msg,*args,**kwargs)

def info(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)

    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    info('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :INFO] test

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.info(msg,*args,**kwargs)


def warning(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for __name__)

    See logging module for *args and **kwargs documentation.

    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    warning('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :WARNING] test

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.warning(msg,*args,**kwargs)
    
def error(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)

    See logging module for *args and **kwargs documentation.

    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    error('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :ERROR] test

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.error(msg,*args,**kwargs)

def critical(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)

    See logging module for *args and **kwargs documentation.

    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    critical('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :CRITICAL] test

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.critical(msg,*args,**kwargs)

def exception(msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)

    See logging module for *args and **kwargs documentation.


    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    try:
    ...       x = []
    ...       print(x[0])
    ...    except IndexError:
    ...       exception('test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :ERROR] test
    Traceback (most recent call last):
      File "<doctest logarhythm.logarhythm.exception[1]>", line 4, in <module>
        print(x[0])
    IndexError: list index out of range

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.exception(msg,*args,**kwargs)

def log(level,msg,*args,**kwargs):
    """
    Logs a message on the default logger (default = logger for \_\_name\_\_)

    See logging module for *args and **kwargs documentation.

    ```
    >>> logger = getLogger()
    >>> with logger.use(doctest_mode=True,level=DEBUG):
    ...    log(DEBUG,'test') #uses same object named logger above, even though this is a module level function and not a Logger method
    ... 
    [logarhythm.logarhythm :DEBUG] test

    ```
    """
    caller_frame_info = inspect.stack()[1]
    name = caller_frame_info[0].f_globals['__name__']
    logger = Logger(name)
    kwargs['caller_frame_info'] = caller_frame_info
    logger.log(level,msg,*args,**kwargs)


class GlobalSettings(object):
    """
    Manages global level settings
    """
    disarm_logging_module = False
    """
    Whether or not the logging module functions are changed to use module level loggers instead of the root logger
    """
    auto_debug_enabled = False
    """
    Whether or not unhandled exceptions will result in entering debug mode
    """
    end_interactive_enabled = False
    """
    Whether or not the script will go into interactive mode when it finishes executing
    """
    _first_load = True

    @classmethod
    def set_auto_debug(klass,value):
        """
        When set to True, enter post-mortem pdb debug mode on unhandled exceptions.

        >>> GlobalSettings.set_auto_debug(True) #auto debug enabled
        >>> GlobalSettings.set_auto_debug(False) #auto debug disabled
        """
        if value is True:
            klass.auto_debug_enabled = True 
            sys.excepthook = _auto_debug_handler
        elif value is False:
            klass.auto_debug_enabled = False 
            sys.excepthook = _default_exception_handler

    @classmethod
    def set_end_interactive(klass,value):
        """
        When set to True, enter interactive mode when script is done processing

        ```
        >>> GlobalSettings.set_end_interactive(True) #will cause interpreter to go to interactive mode when script stops running
        >>> GlobalSettings.set_end_interactive(False) #interpreter will terminate when script stops running

        ```
        """
        if value is True:
            klass.end_interactive_enabled = True
            os.environ['PYTHONINSPECT'] = '1'
        else: #pragma: no cover
            klass.end_interactive_enabled = False 
            if 'PYTHONINSPECT' in os.environ:
                del os.environ['PYTHONINSPECT']
    @classmethod
    def set_disarm_logging_module(klass,value):
        """
        Monkey-patches the logging module to make the default behavior for module level functions to be to grab the module-level logger instead of the root logger.

        This helps to prevent third party modules from broadcasting logging methods on the root logger by following the official basic logging instructions.

        Afffects the following functions:
        - debug
        - info
        - warning
        - error
        - critical
        - exception
        - log
        - getLogger

        This function is automatically called with disarm=True when logarhythm is imported.

        To restore the logging module to normal, call this function with disarm=False

        ```
        >>> GlobalSettings.set_disarm_logging_module(False) #restores the original functions to the logging module
        >>> GlobalSettings.set_disarm_logging_module(True) #replaces the logging module functions with the logarhythm equivalents

        ```
        """
        if value:
            klass.disarm_logging_module = True
            [logging.debug,logging.info,logging.warning,logging.error,logging.critical,logging.exception,logging.log,logging.getLogger] = _disarmed_logging_functions 
        else: #pragma: no cover
            klass.disarm_logging_module = False
            [logging.debug,logging.info,logging.warning,logging.error,logging.critical,logging.exception,logging.log,logging.getLogger] = _default_logging_functions 

set_disarm_logging_module = GlobalSettings.set_disarm_logging_module
set_auto_debug = GlobalSettings.set_auto_debug
set_end_interactive = GlobalSettings.set_end_interactive
#do this only once, otherwise original_getLogger will be overwritten and lost
if not hasattr(logging,'logarhythm_monkey_patched'): #pragma: no cover
    logging.logarhythm_monkey_patched = True
    _default_logging_functions = [logging.debug,logging.info,logging.warning,logging.error,logging.critical,logging.exception,logging.log,logging.getLogger]
    _disarmed_logging_functions = [debug,info,warning,error,critical,exception,log,getLogger_logging_module]
    original_getLogger = logging.getLogger
    logging.original_getLogger = original_getLogger
    GlobalSettings.set_disarm_logging_module(True)
    _default_exception_handler = sys.excepthook


class Logger(object):
    """
    Primary class for logarhythm. All logarhythm functionalities can be accessed from this class.

    When Logger objects are created, they will inherit the following attributes from their parent logger:
        stderr
        stdout
        format_fmt
        format_time_fmt
        format_style

    The root logger has no parent, and will have the following settings by default:
        stderr = True
        stdout = False
    """ 

    NOTSET=NOTSET
    """NOTSET = 0 - Implies a logger uses its parents level"""
    DEBUG=DEBUG
    """DEBUG = 10"""
    INFO=INFO
    """INFO = 20"""
    WARNING=WARNING
    """WARNING = 30"""
    ERROR=ERROR
    """ERROR = 40"""
    CRITICAL=CRITICAL
    """CRITICAL = 50"""
    OFF=OFF
    """OFF = 60"""
    _loggers = {}
    _modes = {item.strip() for item in '''
            dev_mode
            doctest_mode
            prod_mode
            '''.split() if item.strip() != ''}
    _settables = {item.strip() for item in '''
            debugging_disabled
            captures_disabled
            profiling_disabled
            monitoring_disabled
            auto_debug
            end_interactive
            disarm_logging_module
            level
            stderr
            stdout
            format
            '''.split() if item.strip() != ''}
    _monitor_attr_info = {}
    _monitor_func_info = {}
    _monitor_meth_info = {}
    def _default_init(self):
        #initialize handlers/handles
        self._stderr_handler = None
        self._stdout_handler = None
        self._stderr = False
        self._stdout = False
        self._file_handles = {}
        self._special_handles = {}
        self._captures = {}
        self.set_format(*build_format()) #must be done after _stderr_handler and _stdout_handler are initialized
        self.children = {}
        self.debugging_disabled=False
        self.captures_disabled = False
        self.profiling_disabled = False
        self.monitoring_disabled = False



    def __new__(klass,*args,**kwargs):
        #loggers with same name are same object
        if len(args) > 0:
            #name provided as positional arg
            name = args[0]
        elif 'name' in kwargs:
            #name provided as keyword arg
            name = kwargs['name']
        else:
            #by default name uses __name__ of calling context
            caller_frame_info = inspect.stack()[1]
            name = caller_frame_info[0].f_globals['__name__']
        if name is None:
            #by default name uses __name__ of calling context
            caller_frame_info = inspect.stack()[1]
            name = caller_frame_info[0].f_globals['__name__']
        elif name.startswith('.'):
            if len(name) > 1:
                caller_frame_info = inspect.stack()[1]
                name = caller_frame_info[0].f_globals['__name__'] + name
            else:
                caller_frame_info = inspect.stack()[1]
                name = caller_frame_info[0].f_globals['__name__']


        if name in klass._loggers:
            #logger name already exists
            self = klass._loggers[name]
        elif name == '':
            #logger does not exist and is the root logger
            self = root_logger = super(klass,klass).__new__(klass) 
            klass.root_logger = root_logger
            root_logger.parent = None #root logger parent is None
            root_logger._name = name
            klass._loggers[name] = root_logger
            root_logger._logger = original_getLogger() #root logger
            root_logger._logger.propagate = False 
            root_logger._default_init()
            root_logger.stderr = True
            root_logger.stdout = False

        else:
            #logger does not exist and is not the root logger
            self = super(klass,klass).__new__(klass) 
        return self
    def __init__(self,
            name=None,
            **kwargs
            ):
        #default name is __name__ from calling context
        if name is None:
            caller_frame_info = inspect.stack()[1]
            name = caller_frame_info[0].f_globals['__name__']
        elif name.startswith('.'):
            if len(name) > 1:
                caller_frame_info = inspect.stack()[1]
                name = caller_frame_info[0].f_globals['__name__'] + name
            else:
                caller_frame_info = inspect.stack()[1]
                name = caller_frame_info[0].f_globals['__name__']
        if name in self.__class__._loggers:
            #already been created, but changing properties
            self.set(**kwargs)
            return


        self.__class__._loggers[name] = self
        self.children = {}

        if name == '':
            raise LogarhythmException('Unexpected situation - name denotes root logger but normal constructor being called')#pragma: no cover
        else:
            name_pieces = name.split('.')
            if len(name_pieces) == 1:
                parent = self.root_logger
                my_child_name = name
            else:
                parent = Logger('.'.join(name_pieces[:-1]))
                my_child_name = name_pieces[-1]

        self.parent = parent #must be set before name property
        parent.children[my_child_name] = self
        self.name = name #property setter

        self._logger.propagate = False #prevents duplicate logging messages from a child and its parent/ancestors

        #first time creation defaults
        level = kwargs.get('level')
        stderr = kwargs.get('stderr')
        stdout = kwargs.get('stdout')
        if level is None:
            level = NOTSET
        if stderr is None:
            stderr=parent.stderr
        if stdout is None:
            stdout=parent.stdout

        format_fmt=parent._format_fmt
        format_time_fmt=parent._format_time_fmt
        format_style=parent._format_style

        self._default_init()
    
        self.level = level #property setter
        self.set_format(format_fmt,format_time_fmt,format_style) #must be done after handlers initialized
        self.stderr = stderr #property setter, must be done after format()
        self.stdout = stdout #property setter, must be done after format()
        self.set(**kwargs)

    def reinitialize(self,**kwargs):
        """
        Resets all logger settings to the default values then applies the provided keyword arguments to change attributes

        ```
        >>> logger = Logger()
        >>> logger.stdout = True
        >>> logger.reinitialize(stderr=False)
        >>> logger.stdout #stdout default is False
        False
        >>> logger.stderr #stderr default is True, but should be overwritten by keyword arg above
        False
        >>> logger.stderr = True

        ```
        """
        name = self.name
        children = self.children
        del self.__class__._loggers[name]
        for handler in self._handlers():
            self._logger.removeHandler(handler)
        self.__init__(name,**kwargs)
        self.children = children
    def _set(self,**kwargs):
        kws = set(kwargs.keys())
        invalid_kws = kws - (self._settables | self._modes)
        if len(invalid_kws) > 0:
            raise Exception('Invalid keywords: %s' % ', '.join(sorted(invalid_kws)))
        attribute_list = list(kws)
        mode_count = 0
        for a in self._modes:
            if a in kwargs:
                mode_count+=1
                attribute_list.remove(a)
                attribute_list.insert(0,a) #mode attributes should be applied before the corresponding attributes
        if mode_count > 1:
            raise Exception('Cannot set more than one mode at a time')
        for a in attribute_list:
            setattr(self,a,kwargs[a])

        
    def set(self,**kwargs):
        """
        Sets attributes based on keyword arguments for this logger (for the lazy who want to write only one line)

        Valid for the following attributes:
            auto_debug
            captures_disabled
            debugging_disabled
            disarm_logging_module
            end_interactive
            format
            level
            profiling_disabled
            monitoring_disabled
            stderr
            stdout
        """
        
        self._set(**kwargs)
        return self

    def set_all(self,**kwargs):
        """
        Sets attributes based on keyword arguments for this logger and all of its descendant loggers.
        Valid for the attributes listed in the Logger.set() method's documentation..

        ```
        >>> logger = getLogger('doctest')
        >>> grandchild = getLogger('doctest.child.grandchild')
        >>> _=logger.set_all(level=DEBUG)
        >>> grandchild.level == DEBUG
        True
        >>> _=logger.set_all(level=NOTSET)
        >>> grandchild.level == NOTSET
        True

        ```
        """ 
        for logger in self.walk():
            logger._set(**kwargs)
        return self

    @contextmanager
    def use(self,**kwargs):
        """
        Used in a with block.
        Temporarily sets logger attributes based on keyword arguments, then sets them back at the end of the block.
        Valid for the attributes listed in the Logger.set() method's documentation.
        """ 
        snapshot = {a:getattr(self,a) for a in self._settables}
        self._set(**kwargs)
        yield
        self._set(**snapshot)

    @classmethod
    def get_loggers(klass):
        """
        Returns a dictionary mapping all existing logger names to logger objects.

        ```
        >>> logger = getLogger()
        >>> logger.name in Logger.get_loggers()
        True
        >>> root_logger.name in Logger.get_loggers()
        True

        ```
        """
        return dict(klass._loggers)

    def child(self,child_name,*args,**kwargs):
        """
        Returns a child logger given a relative name for the child.

        Positional and keyword arguments are passed into the Logger constructor.


        ```
        >>> logger = Logger('doctest')
        >>> logger2 = root_logger.child('doctest')
        >>> logger is logger2 # shows that named loggers are children of the root logger
        True
        >>> subsys1_logger = logger.child('subsys1')
        >>> unit1_logger = subsys1_logger.child('unit1')
        >>> unit2_logger = subsys1_logger.child('unit2')
        >>> print(unit1_logger.name)
        doctest.subsys1.unit1
        >>> with subsys1_logger.use(level = DEBUG):
        ...   with unit2_logger.use(doctest_mode=True):
        ...     unit2_logger.debug("this shows because parent's level = DEBUG")
        ...   with unit1_logger.use(doctest_mode=True):
        ...     unit1_logger.debug('same here')
        ... 
        [doctest.subsys1.unit2 :DEBUG] this shows because parent's level = DEBUG
        [doctest.subsys1.unit1 :DEBUG] same here
        >>> unit1_logger.debug('this does not show because the parents level was set back to NOTSET')
        >>> with unit1_logger.use(doctest_mode=True,level = INFO):
        ...  unit1_logger.info('this does show')
        ... 
        [doctest.subsys1.unit1 :INFO] this does show
        >>> lower = unit1_logger.child('some.deep.logger')
        >>> print(lower.parent.name)
        doctest.subsys1.unit1.some.deep

        ```

        """
        if self is self.root_logger:
            name = child_name
        else:
            name = self.name + '.' + child_name
        return Logger(name,*args,**kwargs)

    def debug(self,msg,*args,**kwargs):
        """
        Logs a message at level DEBUG. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.debug(msg,*args,**kwargs)
        self._capture_check(DEBUG,msg,args,caller_frame_info)


    def info(self,msg,*args,**kwargs):
        """
        Logs a message at level INFO. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.info(msg,*args,**kwargs)
        self._capture_check(INFO,msg,args,caller_frame_info)


    def warning(self,msg,*args,**kwargs):
        """
        Logs a message at level WARNING. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.warning(msg,*args,**kwargs)
        self._capture_check(WARNING,msg,args,caller_frame_info)


    def error(self,msg,*args,**kwargs):
        """
        Logs a message at level ERROR. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.error(msg,*args,**kwargs)
        self._capture_check(ERROR,msg,args,caller_frame_info)

    def critical(self,msg,*args,**kwargs):
        """
        Logs a message at level CRITICAL. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.critical(msg,*args,**kwargs)
        self._capture_check(CRITICAL,msg,args,caller_frame_info)
    def exception(self,msg,*args,**kwargs):
        """
        Logs a message at level ERROR. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        self._logger.exception(msg,*args,**kwargs)
        self._capture_check(ERROR,msg,args,caller_frame_info)
    def __call__(self,level,msg,*args,**kwargs):
        """
        Same as Logger.log()
        """
        self.log(level,msg,*args,**kwargs)
    def log(self,level,msg,*args,**kwargs):
        """
        Logs a message at the specified level. See logging documentation for args and kwargs information.
        """
        if 'caller_frame_info' in kwargs:
            caller_frame_info = kwargs['caller_frame_info']
            del kwargs['caller_frame_info']
        else:
            try:
                caller_frame_info = inspect.stack()[1]
            except: #pragma: no cover
                caller_frame_info = None
        if 'no_capture_check' in kwargs:
            no_capture_check = kwargs['no_capture_check']
            del kwargs['no_capture_check']
        else:
            no_capture_check = False
        self._logger.log(level,msg,*args,**kwargs)
        if not no_capture_check:
            self._capture_check(level,msg,args,caller_frame_info)


    def clear_captures(self):
        """
        Clears all capture patterns that were registered for this logger
        """
        self._captures = {}

    def capture(self,pattern,flags=0,target_level=None,callback=capture_debug_callback):
        """
        Registers a capture pattern to stop in debug mode when a logging message at the appropriate level matches the provided regular expression.
        Can also execute a custom callback to do some other action.

        ```
        >>> logger = Logger('doctest') 
        >>> logger.capture('is 3')
        >>> logger.capture('some second pattern')
        >>> with logger.use(doctest_mode=True,level=DEBUG):
        ...    for x in range(5):
        ...       logger.debug('x is %d',x)
        ...    logger.clear_captures()
        ...    logger.debug('x is 3')
        ... 
        [doctest :DEBUG] x is 0
        [doctest :DEBUG] x is 1
        [doctest :DEBUG] x is 2
        [doctest :DEBUG] x is 3
        [doctest :WARNING] ALL capture pattern triggered for 'is 3' at <doctest logarhythm.logarhythm.Logger.capture[3]> line 3
        [doctest :DEBUG] x is 4
        [doctest :DEBUG] x is 3

        ```

        """
        regex = re.compile(pattern,flags)
        if not target_level in self._captures:
            self._captures[target_level] = []
        self._captures[target_level].append((regex,callback))

    def _capture_check(self,level,msg,args,caller_frame_info):
        #most of the time this is disabled - so return fast in that case to mitigate performance reduction
        if self.captures_disabled or len(self._captures) == 0 or not self.will_log(level):
            return 
        full_msg = None
        level_names = {None:'ALL',DEBUG:'DEBUG',INFO:'INFO',WARNING:'WARNING',ERROR:'ERROR',CRITICAL:'CRITICAL'}
        for _level in [level,None]:
            if not _level in level_names:
                continue
            level_name = level_names[_level] #OFF excluded
            if _level in self._captures:
                if full_msg is None: #pragma: no cover
                    if len(args) > 0:
                        full_msg = msg % args
                    else:
                        full_msg = msg
                for regex,callback in self._captures[_level]:
                    m = regex.search(full_msg)
                    if m is not None:
                        rep = repr(regex.pattern)
                        if rep.startswith("u'"):
                            rep = rep[1:]
                        if caller_frame_info is not None:
                            self.log(WARNING,'%s capture pattern triggered for %s at %s line %d' % (
                                level_name,
                                rep,
                                caller_frame_info[1],
                                caller_frame_info[2],
                                ),
                                no_capture_check=True,
                            )
                        else: #pragma: no cover
                            self.log(WARNING,'%s capture pattern triggered for %s' % (
                                level_name,
                                rep,
                                ),
                                no_capture_check=True,
                            )
                        callback(self,caller_frame_info,m,_level)
    def will_log(self,level):
        """
        This returns True if a message at the given level would end up getting logged.
        This searches for a logger whose level is something other than NOTSET, starting at the current logger and going up the tree to parent loggers.
        If it encounters a logger with an explicit level, it will return the comparison of the specified level to the level of the logger that was found.
        If all loggers looked at have level=NOTSET, then it will return the comparison of the specified level to WARNING.

        ```
        >>> logger = getLogger()
        >>> logger.will_log(DEBUG)
        False
        >>> root_logger.level = DEBUG
        >>> logger.will_log(DEBUG)
        True
        >>> root_logger.level = NOTSET
        >>> logger.will_log(WARNING)
        True
        >>> logger.will_log(INFO)
        False

        ```
        """
        target = self
        while target is not None:
            #if NOTSET, then go to the parent
            if target.level == NOTSET:
                target = target.parent
            elif target.level <= level:
                #found a logger that will accept the message
                return True
            else:
                #found a logger that will reject the message
                return False
        #all loggers in ancestry chain are NOTSET - default level is WARNING
        if level >= WARNING:
            return True
        else:
            return False


    def breakpoint(self,condition=True,caller_frame_info=None):
        """
        Stops in debug mode when the provided condition is met.

        ```
        >>> logger = Logger('doctest') 
        >>> with logger.use(doctest_mode=True):
        ...    for x in range(100):
        ...       logger.breakpoint(x == 35)
        ... 
        [doctest :WARNING] Breakpoint triggered for Logger at <doctest logarhythm.logarhythm.Logger.breakpoint[1]> line 3

        ```
        """
        if caller_frame_info is None:
            caller_frame_info = inspect.stack()[1]
        if condition is True:
            self.log(WARNING,'Breakpoint triggered for %s at %s line %d' % (
                self.__class__.__name__,
                caller_frame_info[1],
                caller_frame_info[2],
                ),
            no_capture_check=True)
            if not self.debugging_disabled:
                pdb.Pdb().set_trace(caller_frame_info[0]) #pragma: no cover


    @property
    def name(self):
        """
        The logger name
        """
        return self._name
    @name.setter
    def name(self,value):
        self._name = value
        if not hasattr(self,'_logger'): #if logger.reinitialize() is called, this prevents duplicate _logger instances
            self._logger = original_getLogger(value)

    @property
    def auto_debug(self):
        """
        Tied to the global flag for auto_debug. 

        When True, unhandled exceptions will result in entering debug mode.

        """
        return GlobalSettings.auto_debug_enabled
    @auto_debug.setter
    def auto_debug(self,value):
        if value is True:
            GlobalSettings.set_auto_debug(True)
        else:
            GlobalSettings.set_auto_debug(False)

    @property
    def end_interactive(self):
        """
        Tied to the global flag for end_interactive.

        When True, the script will end in interactive mode.
        """
        return GlobalSettings.end_interactive_enabled
    @end_interactive.setter
    def end_interactive(self,value):
        GlobalSettings.set_end_interactive(value)
    @property
    def disarm_logging_module(self):
        """
        Tied to the global flag for end_interactive.

        When True, the logging module will have its top level functions changed to use a module level logger by default instead of the root logger.
        """
        return GlobalSettings.disarm_logging_module
    @disarm_logging_module.setter
    def disarm_logging_module(self,value):
        GlobalSettings.set_disarm_logging_module(value)

    @property
    def level(self):
        """
        Will log messages with levels at or higher than the logger's level
        """
        return self._logger.level
    @level.setter
    def level(self,value):
        self._logger.level = value


    def _handlers(self):
        """
        Yields all logging module handlers attached to this logger.
        """
        if self._stderr_handler is not None:
            yield self._stderr_handler
        if self._stdout_handler is not None:
            yield self._stdout_handler
        for handle in self._file_handles.values():
            yield handle.handler
        for handle in self._special_handles.values():
            yield handle.handler

    @property
    def doctest_mode(self):
        """
        This is a shortcut attribute.
        It always evaluates to False.
        When set to True, it is a shortcut for:

        - .stderr = False
        - .stdout = True
        - .format = build_format(time=None)
        - .debugging_disabled = True

        ```
        >>> logger = getLogger('doctest')
        >>> with logger.use(doctest_mode=True):
        ...  logger.doctest_mode == False
        ... 
        True

        ```
        """
        return False
    @doctest_mode.setter
    def doctest_mode(self,value):
        if value is True:
            self.stderr = False
            self.stdout = True
            self.set_format(*build_format(time=None))
            self.debugging_disabled = True
    @property
    def dev_mode(self):
        """
        This is a shortcut attribute.
        It always evaluates to False.
        When set to True, it is a shortcut for:

        - .stderr = True
        - .stdout = False
        - .auto_debug = True
        - .level = DEBUG
        - .captures_disabled=False
        - .profiling_disabled=False
        - .monitoring_disabled = False
        - .debugging_disabled = False

        ```
        >>> logger = getLogger('doctest')
        >>> with logger.use(dev_mode=True,stderr=False,stdout=True,format=build_format(time=None)):
        ...  logger.debug('debug')
        [doctest :DEBUG] debug
        >>> logger = getLogger('doctest')
        >>> with logger.use(dev_mode=True):
        ...  logger.dev_mode == False
        ... 
        True

        ```
        """
        return False
    @dev_mode.setter
    def dev_mode(self,value):
        self.stderr = True
        self.stdout = False
        self.auto_debug = True
        self.level = DEBUG
        self.captures_disabled = False
        self.profiling_disabled = False
        self.monitoring_disabled = False
        self.debugging_disabled = False
    @property
    def prod_mode(self):
        """
        This is a shortcut attribute.
        It always evaluates to False.

        When set to True, it is a shortcut for:

        - .stderr = True
        - .stdout = False
        - .auto_debug = False
        - .end_interactive_mode = False
        - .level = NOTSET
        - .captures_disabled = True
        - .profiling_disabled = True
        - .monitoring_disabled = True
        - .debugging_disabled = True

        ```
        >>> from time import sleep
        >>> logger = getLogger('doctest')
        >>> with logger.use(prod_mode=True,level=INFO):
        ...  print(logger.prod_mode)
        ...  with logger.profile():
        ...   sleep(0.1) 
        ... 
        False

        ```
        """
        return False
    @prod_mode.setter
    def prod_mode(self,value):
        self.stderr = True
        self.stdout = False
        self.auto_debug = False
        self.end_interactive_mode = False
        self.level = NOTSET
        self.captures_disabled = True
        self.profiling_disabled = True
        self.monitoring_disabled = True
        self.debugging_disabled = True

    @property
    def format(self):
        """
        This is a convenience property functionally equivalent to the set_format() method.
        This should be set to a tuple value that will be used as an argument to set_format().
        Once can assign this property to the value returned by the build_format() function.
        """
        return (self._format_fmt,self._format_time_fmt,self._format_style)
    @format.setter
    def format(self,value):
        self.set_format(*value)

    def set_format(self,fmt=None,time_fmt=None,style=None,handle=None):
        """
        Sets the formatting for handlers.
        The first three arguments are the same as the logging module and are compatible with the output of the logarhythm.build_format() function.

        If handle is None - will apply to all existing handlers and to any that are created in the future.

        If handle == "stdout" or "stderr" will apply to one of those streams.

        Otherwise, if handle is a FileHandle, StreamHandle, or SpecialHandle object, will apply to the associated handler

        ```
        >>> logger = Logger('doctest')
        >>> with logger.use(stderr=False,stdout=True):
        ...    logger.set_format('%(levelname)s - %(msg)s')
        ...    logger.warning('hi')
        ... 
        WARNING - hi
        >>> with logger.use(doctest_mode=True,stdout=True):
        ...    logger.warning('bye')
        [doctest :WARNING] bye

        ```
        """
        if fmt is None:
            fmt = self._format_fmt
        if time_fmt is None:
            time_fmt = self._format_time_fmt
        if style is None:
            style = self._format_style
        if is_py2:#pragma: no cover
            formatter = logging.Formatter(fmt,time_fmt)
        else:
            formatter = logging.Formatter(fmt,time_fmt,style)
        if handle is None: #pragma: no cover
            self._format_fmt = fmt
            self._format_time_fmt = time_fmt
            self._format_style = style
            self._formatter = formatter
            for handler in self._handlers():
                handler.setFormatter(self._formatter)
        elif handle == 'stderr': #pragma: no cover
            if self._stderr_handler is not None:
                self._stderr_handler.setFormatter(formatter)
            else: #pragma: no cover
                raise LogarhythmException('stderr logging is disabled but format is trying to be set')
        elif handle == 'stdout': #pragma: no cover
            if self._stdout_handler is not None:
                self._stdout_handler.setFormatter(formatter)
            else: #pragma: no cover
                raise LogarhythmException('stdout logging is disabled but format is trying to be set')
        elif isinstance(handle,LoggingHandle): #pragma: no cover
            handle.handler.setFormatter(formatter)
        else: #pragma: no cover
            raise LogarhythmException('Invalid handle value for format()')

    @property
    def stderr(self):
        """
        When set to True, messages will be logged to stderr.
        """
        return self._stderr
    @stderr.setter
    def stderr(self,value):
        if value is True and self._stderr is False:
            self._stderr = True
            self._stderr_handler = handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(self._formatter)
            self._logger.addHandler(handler)
        elif value is False and self._stderr is True:
            self._stderr = False 
            if self._stderr_handler is not None:
                self._logger.removeHandler(self._stderr_handler)
            self._stderr_handler = None

    @property
    def stdout(self):
        """
        When set to True, messages will be logged to stdout.
        """
        return self._stdout
    @stdout.setter
    def stdout(self,value):
        if value is True and self._stdout is False:
            self._stdout = True
            self._stdout_handler = handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(self._formatter)
            self._logger.addHandler(handler)
        elif value is False and self._stdout is True:
            self._stdout = False 
            if self._stdout_handler is not None:
                self._logger.removeHandler(self._stdout_handler)
            self._stdout_handler = None

    def stream_open(self,stream=None):
        """
        Configures the logger to log to a StringIO object.
        If one is not provided a new one will be created.

        Returns a logarhythm.StreamHandle object.
        The StringIO object is present as the stream attribute of the StreamHandle object.
        The StreamHandle object also has a getvalue() method that returns the string context of the StringIO object.

        The StreamHandle object can be used as a context manager. When the context block ends, the logger will no longer
        log messages to the StreamHandle

        ```
        >>> logger = Logger('doctest')
        >>> with logger.use(stdout=False,doctest_mode=True,level=DEBUG):
        ...    with logger.stream_open() as sh:
        ...       logger.debug('hello world')
        ... 
        ...
        >>> print(sh.getvalue().strip())
        [doctest :DEBUG] hello world

        ```

        """
        if stream is None: #pragma: no cover
            stream = StringIO()
        sh = StreamHandle(self,stream)
        sh.handler.setFormatter(self._formatter)
        handle_key = len(self._special_handles)
        self._special_handles[handle_key] = sh
        sh.handle_key = handle_key
        self._logger.addHandler(sh.handler)
        return sh

    def file_open(self,path,mode='a',encoding=None,delay=False):
        """
        Opens a file and starts logging messages to it.
        Returns a FileHandle object.

        ```
        >>> logger = Logger('doctest')
        >>> with logger.use(stdout=False,doctest_mode=True):
        ...    with logger.file_open('test.log','w') as fh:
        ...       logger.error('this goes to the file')
        ...    
        >>> with open('test.log','r') as f:
        ...    print(f.read().strip())
        ... 
        [doctest :ERROR] this goes to the file
        >>> os.remove('test.log')

        ``` 

        """
        if path in self._file_handles:
            raise LogarhythmException('File already opened for path: %s' % path) #pragma: no cover
        fh = FileHandle(self,path,mode,encoding,delay)
        fh.handler.setFormatter(self._formatter)
        self._file_handles[path] = fh 
        self._logger.addHandler(fh.handler)
        return fh

    def _file_close(self,fh):
        self._logger.removeHandler(fh.handler)
        del self._file_handles[fh.path]

    def handler_add(self,handler,use_logger_formatter=True):
        """
        Add a handler from the standard logging module to the logarhythm module. 
        This can be used to provide the full flexibility of the standard logging module for special handlers like rotating file handlers, socket handlers, etc.

        The optional parameter use_logger_formatter, when set to True will change the formatting of added handler to match the logarhythm logger's.
        If set to False, then whatever formatter the provided handler was configured with will be used.

        ```
        >>> sio = StringIO()
        >>> s = logging.StreamHandler(sio)
        >>> fh = logging.FileHandler('test_handler_add.log',mode='w')
        >>> logger = Logger('doctest')
        >>> with logger.use(level=DEBUG,stdout=False,doctest_mode=True):
        ...    sh = logger.handler_add(s)
        ...    sh2 = logger.handler_add(fh,use_logger_formatter=False)
        ...    logger.debug('test')
        ... 
        >>> sh.close()
        >>> sh2.close()
        >>> print(sio.getvalue().strip())
        [doctest :DEBUG] test
        >>> with open('test_handler_add.log','r') as f:
        ...    print(f.read().strip())
        ... 
        test
        >>> os.remove('test_handler_add.log')

        ```
        """
        sh = SpecialHandle(self,handler)
        if use_logger_formatter:
            handler.setFormatter(self._formatter)
        self._logger.addHandler(handler)
        handle_key = len(self._special_handles)
        self._special_handles[handle_key] = sh
        sh.handle_key = handle_key
        return sh
        
    def _special_handle_remove(self,sh):
        if sh.handle_key not in self._special_handles: #pragma: no cover
            raise LogarhythmException('Attempt to remove non-existent handle key: %s' % repr(handle_key))
        self._logger.removeHandler(sh.handler)
        del self._special_handles[sh.handle_key]

    def walk(self):
        """
        Iterates through this logger and all of its descendants (i.e. children, children's children, etc)
        """
        yield self
        for child_name, child_logger in sorted(self.children.items()):
            for desc_logger in child_logger.walk():
                yield desc_logger

    def monitor_attr(self,target,attr_name=None,label=None,level=DEBUG,callback=None):
        """
        Monitors an object for attribute changes.
        If attr_name is specified, only that attribute will be monitored.
        If attr_name is unspecified, all attributes that do not begin with "_" will be monitored for that object.

        When a change happens to a monitored attribute, a log message at the specified level will be generated.
        If a label was specified, this label will be included in the log message.
        If a callback was specified, this callback will be called.
        The callback arguments match the monitor_attr_debug_callback() function - see that function for more details.

        To remove monitoring on an object, use the unmonitor() method.

        ```
        >>> logger = getLogger('doctest')
        >>> class Bunch(object): pass
        ... 
        >>> b = Bunch()
        >>> b.x = 1
        >>> b.y = 'this is a quite long string that will be summarized in some way that you will see below'
        >>> with logger.use(doctest_mode=True,level=DEBUG):
        ...  logger.monitor_attr(b,'x')
        ...  logger.monitor_attr(b,'y',label='watching y',callback=monitor_attr_debug_callback)
        ...  b.x = 10
        ...  b.y += ' after this variable changes'
        ...  logger.unmonitor(b)
        ...  b.x = 900
        ... 
        [doctest :DEBUG] Monitored attribute set .x from 1 to 10
        [doctest :DEBUG] Monitored attribute set .y from 'this is a quite... will see below' to 'this is a quite...ariable changes' (label="watching y")

        ```
        """


        if self.monitoring_disabled:
            return

        #The goal is to replace __setattr__ with a function that does the monitoring
        #Multiple loggers might choose to monitor the attribute(or even the same logger registering multiple callbacks)
        #If one logger unmonitors the attribute, it should not effect the monitoring of other loggers, but should remove all associations with the given logger
        

        #To implement this, the first time an object is monitored will result in a change in class for that object.
        #Information will be stored in the Logger._monitor_attr_info variable to make the monitoring work.
        #Subsequent monitor requests will not change the class, but will instead add more info to the _monitor_attr_info variable.
        #When unmonitoring happens, information will be removed from the _monitor_attr_info variable.
        #When there is no more information in the _monitor_attr_info variable, the class of the object will be restored to what it was before.


        logger = self
        target_id = id(target)
        if not isinstance(target,MonitoredAttrItem):
            orig_set_attr = target.__setattr__
            orig_class = target.__class__
            if not target_id in Logger._monitor_attr_info:
                Logger._monitor_attr_info[target_id] = [[],orig_set_attr,orig_class,None]
            Logger._monitor_attr_info[target_id][0].append((logger,attr_name,label,level,callback))
            def monitored_set_attr(self,requested_attr_name,value):
                for logger,attr_name,label,level,callback in Logger._monitor_attr_info[target_id][0]:
                    if logger.monitoring_disabled:
                        logger.unmonitor(self)
                        continue
                    if (attr_name is None and not requested_attr_name.startswith('_')) or requested_attr_name == attr_name:
                        old_value = getattr(self,requested_attr_name)
                        if label is None:
                            logger.log(level,'Monitored attribute set .%s from %s to %s' % (requested_attr_name,short_repr(old_value),short_repr(value)))
                        else:
                            logger.log(level,'Monitored attribute set .%s from %s to %s (label="%s")' % (requested_attr_name,short_repr(old_value),short_repr(value),label))
                        if callback is not None:
                            caller_frame_info = inspect.stack()[1]
                            callback(logger,caller_frame_info,self,requested_attr_name,old_value,value)
                orig_set_attr(requested_attr_name,value)
            mon_class = type(str(target.__class__.__name__+'_mon'),(target.__class__,MonitoredAttrItem),{'__setattr__':monitored_set_attr})
            Logger._monitor_attr_info[target_id][-1] = mon_class
            target.__class__ = mon_class
        else:
            Logger._monitor_attr_info[target_id][0].append((logger,attr_name,label,level,callback))

    
    def monitor_call(self,target_callable,label=None,level=DEBUG,callback=None):
        """
        Monitors an callable object for calls.

        When the monitored object is called, a log message at the specified level will be generated.
        If a label was specified, this label will be included in the log message.
        If a callback was specified, this callback will be called.
        The callback arguments match the monitor_call_debug_callback() function - see that function for more details.

        To remove monitoring on an object, use the unmonitor() method.

        ```
        >>> logger = getLogger('doctest')
        >>> logger2 = getLogger('doctest2')
        >>> def f(x): # test a pure function
        ...  return x**2
        ... 
        >>> class A(object):
        ...  def __call__(self,x): #test an instance with the __call__ method
        ...   return x**3
        ...  @classmethod
        ...  def g(klass,x): #test a class method
        ...   return 5*x
        ...  @staticmethod
        ...  def h(x): #test a static method
        ...   return 30-x
        >>> def c():
        ...  w = 50
        ...  def b(x): #test a function with a closure
        ...   return w + x
        ...  return b
        ... 
        >>> b = c()
        >>> a = A()
        >>> with logger.use(doctest_mode=True,level=DEBUG):
        ...  with logger2.use(doctest_mode=True,level=DEBUG):
        ...   logger.monitor_call(f)
        ...   logger2.monitor_call(f) # multiple loggers monitoring the same item
        ...   f(5)
        ...   logger.unmonitor(f) # unmonitoring for one logger does not effect the other logger
        ...   f(6)
        ...   logger2.unmonitor(f)
        ...   logger.monitor_call(f,label='watching f')
        ...   f(7)
        ...   logger.monitor_call(a,callback=monitor_call_debug_callback)
        ...   logger2.monitor_call(a)
        ...   a(3)
        ...   logger.monitor_call(a.g)
        ...   logger2.monitor_call(a.g)
        ...   a.g(3)
        ...   logger.monitor_call(a.h)
        ...   logger2.monitor_call(a.h)
        ...   a.h(10)
        ...   logger.unmonitor(a)
        ...   logger.unmonitor(a.g)
        ...   logger.unmonitor(a.h)
        ...   logger2.unmonitor(a)
        ...   logger2.unmonitor(a.g)
        ...   logger2.unmonitor(a.h)
        ...   a(3)
        ...   a.g(3)
        ...   a.h(10)
        ...   logger.monitor_call(b)
        ...   logger2.monitor_call(b)
        ...   b(29)
        ...   logger.unmonitor(b)
        ...   b(30)
        ...   logger2.unmonitor(b)
        ...   b(31)
        ... 
        [doctest :DEBUG] Monitored callable called f()
        [doctest2 :DEBUG] Monitored callable called f()
        25
        [doctest2 :DEBUG] Monitored callable called f()
        36
        [doctest :DEBUG] Monitored callable called f() (label="watching f")
        49
        [doctest :DEBUG] Monitored callable called A.__call__()
        [doctest2 :DEBUG] Monitored callable called A.__call__()
        27
        [doctest :DEBUG] Monitored callable called A.g()
        [doctest2 :DEBUG] Monitored callable called A.g()
        15
        [doctest :DEBUG] Monitored callable called h()
        [doctest2 :DEBUG] Monitored callable called h()
        20
        27
        15
        20
        [doctest :DEBUG] Monitored callable called b()
        [doctest2 :DEBUG] Monitored callable called b()
        79
        [doctest2 :DEBUG] Monitored callable called b()
        80
        81

        ```
        """

        #There are two distinct cases that require individual consideration.
        #Case 1: Pure function, static method, class method - monitor all calls to these functions
        #Case 2: normal instance method or instance itsefl that has a call method- monitor calls only for the targeted bounded instance
        #With case 1, we can modify the function itself because the change is desired for all calls to the function regardless of circumstance.
        #With case 2, we want to modify the instance the method is bound to because monitoring is only for calls to that specific instance's method.

        #For case 1, we can change the behavior of the function by replacing its __code__ object. In order to do this, the closures and free variables of the new and old functions/code object must match. These variables cannot be directly constructed but need to be built by creating functions. The approach here is to construct a minial function that calls a Logger dispatch function with some minimal necessary identifying information to fulfill the logging/callback functionality without changing the input/output/side-effect behavior of the monitored function.

        #For case 2, we can take a similar approach as monitor_attr() and change the class of the monitored object with the method of interest being overwritten.


        if self.monitoring_disabled:
            return
        logger = self
        if inspect.isfunction(target_callable) or (inspect.ismethod(target_callable) and inspect.isclass(target_callable.__self__)):
            #Case 1: pure function, static method, or class method
            if inspect.ismethod(target_callable):
                effective_target_callable = target_callable.__func__
                orig_class = [klass for klass in inspect.getmro(target_callable.__self__) if not issubclass(klass,(MonitoredAttrItem,MonitoredMethItem))][0]
                callable_name = orig_class.__name__ + '.' + target_callable.__name__
            else:
                effective_target_callable = target_callable
                callable_name = target_callable.__name__
            target_id = id(effective_target_callable)
            if target_id not in Logger._monitor_func_info:
                orig_code = target_callable.__code__
                closure_vars = {}
                if target_callable.__closure__ is not None:
                    for name,cell in zip(target_callable.__code__.co_freevars,target_callable.__closure__):
                        value = cell.cell_contents
                        closure_vars[name] = value
                exec('''
def closure({0:s}):
    def monitored_func(*args,**kwargs):
        closure_vars = [{0:s}]
        return Logger._monitor_func_dispatch({1:d},*args,**kwargs)
    return monitored_func
monitored_func = closure({0:s})
'''.format(','.join(closure_vars.keys()),target_id),globals(),closure_vars)
                new_code = closure_vars['monitored_func'].__code__
                effective_target_callable.__code__ = new_code
                Logger._monitor_func_info[target_id] = [[],target_callable,effective_target_callable,callable_name,orig_code,new_code]
            Logger._monitor_func_info[target_id][0].append((logger,label,level,callback))

        elif inspect.ismethod(target_callable) or hasattr(target_callable,'__call__'):
            #Case 2: Instance method or instance itself that has a __call__ method 
            if hasattr(target_callable,'__call__'):
                target_callable = target_callable.__call__
            target = target_callable.__self__
            method_name = target_callable.__name__
            if not isinstance(target,MonitoredMethItem): 
                orig_meth = target_callable
                orig_class = target.__class__
                logger = self
                target_id = id(target)
                if not target_id in Logger._monitor_meth_info:
                    Logger._monitor_meth_info[target_id] = [{},orig_class,None]
                if not method_name in Logger._monitor_meth_info[target_id][0]:
                    Logger._monitor_meth_info[target_id][0][method_name] = [[],orig_meth,None]
                Logger._monitor_meth_info[target_id][0][method_name][0].append((logger,label,level,callback))
                funcdef_locals = {}
                exec('''
def monitored_meth(self,*args,**kwargs):
    target_id = id(self)
    method_name = "%s"
    methods,orig_class,mon_class = Logger._monitor_meth_info[target_id]
    entries,orig_meth,mon_meth = methods[method_name]
    for logger,label,level,callback in entries:
        if logger.monitoring_disabled:
            logger.unmonitor(self)
            continue
        if label is None:
            logger.log(level,'Monitored callable called %%s()' %% (orig_class.__name__+'.'+orig_meth.__name__))
        else:
            logger.log(level,'Monitored callable called %%s() (label="%%s")' %% (orig_class.__name__+'.'+orig_meth.__name__,label))
        if callback is not None:
            caller_frame_info = inspect.stack()[1]
            callback(logger,caller_frame_info,orig_meth,args,kwargs)
    return orig_meth(*args,**kwargs)
                ''' % method_name,globals(),funcdef_locals)
                monitored_meth = funcdef_locals['monitored_meth']
                monitored_meth.__name__ = method_name
                mon_class = type(str(target.__class__.__name__+'_mon'),(orig_class,MonitoredMethItem),{method_name:monitored_meth})
                Logger._monitor_meth_info[target_id][-1] = mon_class
                Logger._monitor_meth_info[target_id][0][method_name][-1] = monitored_meth
                target.__class__ = mon_class
            else:
                target_id = id(target)
                orig_meth = target_callable
                methods,orig_class,mon_class = Logger._monitor_meth_info[target_id]
                if method_name in methods:
                    methods[method_name][0].append((logger,label,level,callback))
                else:
                    methods[method_name] = [(logger,label,level,callback),orig_meth,None]
                    def monitored_meth(self,*args,**kwargs):
                        target_id = id(self)
                        method_name = inspect.stack()[0][3]
                        methods,orig_class,mon_class = Logger._monitor_meth_info[target_id]
                        orig_meth = methods[method_name][1]
                        for logger,label,level,callback in methods[method_name][0]:
                            if logger.monitoring_disabled:
                                logger.unmonitor(self)
                                continue
                            if label is None:
                                logger.log(level,'Monitored callable called %s()' % (callable_name))
                            else:
                                logger.log(level,'Monitored callable called %s() (label="%s")' % (callable_name,label))
                            if callback is not None:
                                caller_frame_info = inspect.stack()[1]
                                callback(logger,caller_frame_info,target_callable,args,kwargs)
                        return orig_meth(*args,**kwargs)
                    methods[method_name][-1] = monitored_meth
                    monitored_meth.__name__ = method_name
                    all_methods = {method_name:methods[method_name][-1] for method_name in methods}
                    mon_class = type(str(target.__class__.__name__+'_mon'),(orig_class,MonitoredMethItem),all_methods)
                    Logger._monitor_meth_info[target_id][-1] = mon_class
                    target.__class__ = mon_class


    @staticmethod
    def _monitor_func_dispatch(target_id,*args,**kwargs):
        (entries,target_callable,effective_target_callable,callable_name,orig_code,new_code) = Logger._monitor_func_info[target_id]
        for (logger,label,level,callback) in entries:
            if logger.monitoring_disabled:
                logger.unmonitor(target_callable)
                continue
            if label is None:
                logger.log(level,'Monitored callable called %s()' % (callable_name))
            else:
                logger.log(level,'Monitored callable called %s() (label="%s")' % (callable_name,label))
            if callback is not None:
                caller_frame_info = inspect.stack()[1]
                callback(logger,caller_frame_info,target_callable,args,kwargs)
        effective_target_callable.__code__ = orig_code
        result = effective_target_callable(*args,**kwargs)
        effective_target_callable.__code__ = new_code
        return result


    def unmonitor(self,target):
        """
        Removes all monitoring on an object with respect to this logger for which monitor_attr() or monitor_call() was used on.
        """
        if isinstance(target,MonitoredAttrItem):
            target_id = id(target)
            entries,orig_set_attr,orig_class,mon_class = Logger._monitor_attr_info[target_id]
            new_entries = [entry for entry in entries if entry[0] is not self]
            if len(new_entries) == 0:
                target.__class__ = orig_class
                del Logger._monitor_attr_info[target_id]
            else:
                Logger._monitor_attr_info[target_id] = new_entries

            
        if inspect.isfunction(target) or (inspect.ismethod(target) and inspect.isclass(target.__self__)):
            #pure function, static method, or class method
            if inspect.ismethod(target):
                effective_target_callable = target.__func__
            else:
                effective_target_callable = target
            target_id = id(effective_target_callable)
            if target_id in Logger._monitor_func_info:
                entries,target_callable,effective_target_callable,callable_name,orig_code,new_code = Logger._monitor_func_info[target_id]
                new_entries = [entry for entry in entries if entry[0] is not self]
                if len(new_entries) > 0:
                    Logger._monitor_func_info[target_id][0] = new_entries
                else:
                    effective_target_callable.__code__ = orig_code
                    del Logger._monitor_func_info[target_id]

        elif inspect.ismethod(target) or hasattr(target,'__call__'):
            #bound instance method
            if hasattr(target,'__call__'):
                target= target.__call__
            target_callable = target
            target = target_callable.__self__
            method_name = target_callable.__name__
            target_id = id(target)

            methods,orig_class,mon_class = Logger._monitor_meth_info[target_id]
            if method_name in methods:
                entries,orig_meth,mon_meth = methods[method_name]
                new_entries = [entry for entry in entries if entry[0] is not self]
                if len(new_entries) > 0:
                    methods[method_name][0] = new_entries
                else:
                    del methods[method_name]
                    all_methods = {method_name:methods[method_name][1] for method_name in methods}
                    if len(all_methods) > 0:
                        mon_class = type(str(target.__class__.__name__+'_mon'),(orig_class,MonitoredMethItem),all_methods)
                        Logger._monitor_meth_info[target_id][-1] = mon_class
                        target.__class__ =  mon_class
                    else:
                        del Logger._monitor_meth_info[target_id]
                        target.__class__ = orig_class

    @contextmanager
    def profile(self,label=None,level=INFO):
        """
        Context manager for use with with statement.
        Will profile code within the corresponding with block and generate a log message with the profiling results.

        ```
        import logarhythm
        logger = logarhythm.getLogger()
        logger.level = logarhythm.INFO
        with logger.profile():
           do_some_slow_function()
        #profiling results will be emitted as a logging message here
        ```

        """
        do_it = not self.profiling_disabled and self.will_log(INFO)
        if do_it:
            pr = profile.Profile()
            pr.enable()
        yield
        if do_it:
            pr.disable()
            s = StringIO()
            pstats.Stats(pr,stream=s).sort_stats('cumulative').print_stats()
            border = '='*70
            if label is not None:
                self.log(level,('\n%s\nProfiling Summary "%s":\n%s\n%s' % (border,label,s.getvalue(),border)))
            else:
                self.log(level,('\n%s\nProfiling Summary:\n%s\n%s' % (border,s.getvalue(),border)))

if GlobalSettings._first_load:
    root_logger = Logger(name='')
    root_logger.__doc__ = 'The root logger is the top-level logger in the logger tree. If all loggers have level=NOTSET, then changing the level of the root logger will effectively set the level of all loggers that exist in the python session.'

class LoggingHandle(object):
    """
    Base class for logging handles (controlling a message output target like a file)
    """
    def __init__(self,logger):
        self.logger = logger
    def __del__(self):
        self.close()
    def close(self):
        """Base class method to be overridden by subclasses"""
        raise NotImplementedError
    def __enter__(self):
        return self
    def __exit__(self,exc_type,exc_value,exc_traceback):
        self.close()

class SpecialHandle(LoggingHandle):
    """
    The result of calling logger.handler_add() with some logging module handler
    """
    def __init__(self,logger,handler):
        super(SpecialHandle,self).__init__(logger)
        self.handler = handler
        #assumes logger will set self.handle_key

    def close(self):
        """
        When closed, the logger will no longer write to this handler.
        """
        if self.handler is not None:
            self.logger._special_handle_remove(self)
            if hasattr(self.handler,'close'): #pragma: no cover
                self.handler.close()
            self.handler = None

class StreamHandle(LoggingHandle):
    """
    A handle that represents a StringIO object which has logging messages being written to it
    """
    def __init__(self,logger,stream):
        super(StreamHandle,self).__init__(logger)
        self.stream = stream
        self.handler = logging.StreamHandler(stream)

    def close(self):
        """
        When closed, the logger will no longer write to this stream.
        
        The underlying StringIO object is not closed/destroyed.
        """
        if self.handler is not None:
            self.logger._special_handle_remove(self)
            self.handler = None

    def getvalue(self):
        """
        Returns the string data in the underlying StringIO object.
        """
        return self.stream.getvalue()

class FileHandle(LoggingHandle):
    """
    A handle that represents a file object which has logging messages written to it
    """
    def __init__(self,logger,path,mode='a',encoding=None,delay=None):
        super(FileHandle,self).__init__(logger)
        self.path = path
        self.mode =  mode
        self.encoding = encoding
        self.delay = delay
        self.handler = logging.FileHandler(path,mode=mode,encoding=encoding,delay=delay)
    def close(self):
        """
        When closed, the logger will no longer write to the file and the file itself will be closed.
        """
        if self.handler is not None:
            self.logger._file_close(self)
            self.handler = None
class MonitoredAttrItem(object):
    """
    Base class to indicate that an object has had monitor_attr() called on it.
    """
    pass
class MonitoredMethItem(object):
    """
    Base class to indicate that an object has had monitor_call() called on one of its methods
    """
GlobalSettings._first_load = False


