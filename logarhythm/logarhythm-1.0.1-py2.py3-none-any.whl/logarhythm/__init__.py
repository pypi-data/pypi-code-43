"""
[View API documentation](http://htmlpreview.github.io/?https://github.com/mmiguel6288code/logarhythm/blob/master/docs/logarhythm/logarhythm.html)

## Goals
The goals of this module are to:
    
1. Make it hassle free to set up logging in the recommended way for the most common configurations

2. Provide some ways of using logging to support debugging, data collection (telemetry), and profiling

## Logging Improvements

### The default logger should be __name__ not the root logger
The recommended convention for naming and organizing loggers in the logging HOWTO documentation is to use \_\_name\_\_

i.e. 
```
logger = logging.getLogger(__name__)
```

However, the default logger returned  when no name is provided is the root logger. This can introduce problems because changing settings for the root logger can affect all loggers at every level which may result in seeing unexpected logging messages from imported libraries if those libraries were not careful to set up their logging correctly.
Having messages from libraries can inhibit troubleshooting and development of the package or module of interest to the developer.

Logarhythm resolves this by changing the behavior of the logging module when logarhythm is first loaded. logarhythm replaces the logging module-level functions with versions that use __name__ to determine the default logger instead of returning the root logger. The result of this is that badly behaved third party libraries will use these replaced functions which will return loggers specific to the library and prevent logging messages from being mixed together unless deliberately set to do so.

It is possible to undo this and restore the original logging module functions by calling logarhythm.set_disarm_logging_module(False).


### Hassle-free logging to stdout/stderr/files/streams

To make a logger send messages to an additional streams or files in the standard logging module, one needs to perform several steps including creating one or more handlers, creating formatters, associating each handler with the correct formatter, and adding the handlers to the logger. While this allows for powerful customization, doing the most common situations of stderr/stdout/file/stream should be simpler (i.e. one line).

With logarhythm, to turn on logging to stderr or stdout, simply toggle the corresponding property:

```
logger = logarhythm.getLogger() # corresponds to \_\_name\_\_ by default
logger.stderr = False # turn off logging to stderr (it is on by default)
logger.stdout = True # turn on logging to stdout (it is off by default)
```

For logging to a file, the procedure is similar to how to normally open files in python:

```
logger = logarhythm.getLogger() # corresponds to \_\_name\_\_ by default

# can use as a context manager (closes file and stops logging at end of block)
with logger.file_open('/path/to/file.log'):
    logger.warning('goes to the file') 

# can use with a logarhythm file handle object
fh = logger.file_open('/path/to/file.log')
logger.warning('this also goes to the file')
fh.close() # closes file and stops logging
```

Streams are handled similarly to files:
```
logger = logarhythm.getLogger() # corresponds to \_\_name\_\_ by default

#can use with a context manager (stops logging to stream at end of block)
with logger.stream_open() as sh: 
    logger.warning('goes to the stream')
print(sh.getvalue()) # prints the content of the stream


from io import StringIO
sio = StringIO()
sh = logger.stream_open(sio)
logger.warning('goes to the stream')
sh.close() # stops future logging to stream - does not clear/release the stream itself
assert(sio.getvalue() == sh.getvalue())
```

### Simplified formatting

In the standard logging module, every handler must be individually associated with a formatter object via the setFormatter() method. Additionally, for most people, writing the format string requires reviewing the online documentation to determine what formatting variables are present, since these variable names have inconsistent capitalization and non-straightforward names. Finally one must decide how to order all the desired information the format string, and may end up doing this inconsistently from project to project since there is no standard/default way of constructing these strings.

In logarhythm, each logger has a format assigned to it, and all handlers by default will use the same format. It is still possible in logarhythm to individually assign formatters to handlers if that flexibility is desired. Additionally, there is a utility function called build_format() to automatically construct format strings based on input parameters that specify what information to include or not. These parameters and the valid settings are available by calling help(logarhythm.build_format).

With build_format(), one can choose to include time as 

- "full" = YYYY-MM-DD/hh:mm:ss

- "hms" = hh:mm:ss

- "elapsed_msec" = number of milliseconds since the logging module or logarhythm was loaded

- None = no time

Additionally, one can add or remove via True/False flags the following information:

- logger_name (default True)

- process_name (default False - useful for multiprocessing)

- thread_name (default False - useful for multithreading)

- level (default True)

To apply a format to a logger:
```
logger = logarhythm.getLogger()
logger.format = build_format(time='elapsed_msec',process_name=True)
```

### Logger configuration convenience functions
#### Mode properties
The main rationale for using logging as opposed to print statements is that it gives you the power to turn on or off different levels of diagnostic detail depending on where you are in development. In the quest to make the common situation easier, there are a few special attributes that configure multiple aspects of a given logger into a mode to match a development phase.

The dev_mode property configures the following logger properties suited for development and/or troubleshooting:
    .stderr = True #log messages are displayed and go to stderr
    .stdout = False
    .auto_debug = True #auto debug (post-mortem for unhandled exceptions) is turned on
    .level = DEBUG #debug level messages will show
    .captures_disabled=False #capture patterns are enabled
    .profiling_disabled=False #profiling is enabled
    .monitoring_disabled=False #monitoring is enabled
    .debugging_disabled=False #debugging through logarhythm breakpoints/captures/callbacks is enabled

The prod_mode property reduces/eliminates diagnostic data as possible to make the program suitable for production and external users:
    .stderr = True #log messages are displayed and go to stderr
    .stdout = False
    .auto_debug = False #automatic debug is disabled
    .end_interactive_mode = False #ending in interactive mode is disabled
    .level = NOTSET #all loggers are at the NOTSET level by default (only WARNINGS and higher level messages are displayed)
    .captures_disabled = True #capture patterns are disabled
    .profiling_disabled = True #profiling is disabled
    .monitoring_disabled = True #monitoring is disabled
    .debugging_disabled = True #debugging through logarhythm breakpoints/captures/callbacks is disabled

For writing doctests in which it is desired to include logging messages, the doctest_mode is provided.
    .stderr = False #doctests do not capture stderr, so this is disabled
    .stdout = True #doctests capture stdout, so this is enabled
    .format = build_format(time=None) #this removes timestamps which allows for test repeatability
    .debugging_disabled = True #typically debug mode is not wanted when doctests are being run

#### set(), set_all(), and use()

The following properties/attributes can be set en masse with the set() function using them as keyword arguments.
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

The set_all() function is the same as set() except it applies the values to the current logger as well as all descendant loggers in the logger tree.

The use() function temporarily sets these properties to values with the context of a 'with' block. At the end of the block, all attributes are set back to what they were before the 'with' block.

## Utilities to use logging to support debugging (with pdb)

### Captures
With logarhythm, one can associate a capture pattern (regular expression) that can be triggered when the pattern matches a generated log message.
The capture pattern can be specified with a callback to perform any kind of function, however the default behavior is to enter debug mode.

```
logger = logarthyhm.getLogger()
logger.capture('is 41')
logger.level = DEBUG
for x in range(100):
  logger.debug('x is %d',x) # will enter debug mode when x is 41
```

### Monitoring
With logarhythm, one can mark an object's attribute to be monitored for changes. When the attribute is changed, a log message will be generated and an optional callback, if specified, will be called.
```
logger = logarhythm.getLogger()
obj.x = 5
logger.monitor_attr(obj,'x')
obj.x = 6 # generates a logging message
```

Additionally, one can mark a callable (function, object method, class method, static method, or object with __call__() defined) to be monitored. When the callable is called, a log message will be generated, and an optional callback, if specified will be called.

```
logger = logarhythm.getLogger()
logger.monitor_call(func)
func() # generates a logging message
```

### Miscellaneous convenience utilities
These items are admittedly not directly related to logging, however they are very useful for development and are included for convenience.

## Auto Debug
One useful feature in python for development is to automatically enter debug mode (post-mortem) following an unhandled exception.
This allows one to use pdb to examine the variables at the time of failure in the failed context as well as in calling stack frames (with the "up" command in pdb).
To do this in standard python requires importing several modules, writing a handler function using it to replace the default exception handling hook.

In logarhythm, one can use this feature by calling:
```
import logarhythm;
logarhythm.set_auto_debug(True)
```

## End in Interactive Mode
Once a program has finished running it is common during development to occasionally want to inspect or examine some of the generated variables.
By default, a python program will terminate when it is finished executing. This can be frustrating for Windows users because the command line window simply disappears if the script was not run from an existing command line instance. Additionally, it can be useful for users on any platform in general to end in interactive mode to write doctests (see the doctestify package on pypi for more convenience functions for making doctests).

In logarhythm, one can make a script end in interactive mode by calling:
```
import logarhythm;
logarhythm.set_end_interactive(True)
```
## breakpoint() function
When debugging, one can programmatically enter debug mode by calling pdb.set_trace(). In Python 3.7 additionally a built-in breakpoint() function was introduced to do the same thing.
logarhythm provides a similar function for convenience with two extra caveats:

1) the breakpoint() function can take an optional condition e.g. breakpoint(x==41)
    
2) when invoked, a logging message will be generated saying that a breakpoint was tripped
        

## Utilities for capturing data from your programs

### Capturing structured data (telemetry)
Logarhythm provides two special functions to store and retrieve structure data to and from log files.
The tlm() function takes multiple keyword arguments and values and encodes it into a message that can be sent via one of the logging commands.
Given a collection of logging messages that include some of these tlm messages - the parse_tlm function can locate, extract and decode the tlm data points into dictionaries of key-value pairs.
Both functions allow an optional tlm_channel field, which is a string label that can be used to filter on specific messages.

```
logger.level = INFO
with logger.stream_open() as sh:
    logger.info(tlm('channel A',x=5,y=10))
    logger.info(tlm('channel A',x=9,y=11))
    logger.info(tlm(z='trying to be tricky with )00000000_tlm_end inside the data itself'))

assert(list(parse_tlm(sh.getvalue())) == [{'x':5,'y':10},{'x':9,'y':11},{'z':'trying to be tricky with )00000000_tlm_end inside the data itself'}])
assert(list(parse_tlm(sh.getvalue(),'channel A')) == [{'x':5,'y':10},{'x':9,'y':11}])
``` 

### Profiling
The python standard library comes with some profiling modules to help identify performance bottlenecks in code.
logarhythm provides a convenience function that can wrap around a code block to assess performance within that code block and generate a logging message containing the results.
```
logger.level = INFO
with logger.profile():
    do_some_slow_function()
```
"""
from .logarhythm import *
