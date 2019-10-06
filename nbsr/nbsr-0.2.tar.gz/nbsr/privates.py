"""NBSR private methods in a Mixin class"""


import sys
import queue
import re
import functools
import inspect
from wrapt import decorator
from .exceptions import StreamUnexpectedlyClosed, _TimeOutOccured, rePatternError
from .returnbys import *


def _separate_args(wrapped, wrapped_argslen, wrapper_args_def, args, kwargs):
    """Separate wrapper and wrapped function arguments
    
    Args:
        wrapped (function object): the wrapped function
        wrapped_argslen (int): the length of the wrapped function args
        wrapper_args_def (tuple): definition of list of arguments which are used by
            the wrapper only. Each such argument is defined by a dict with keys of
            ``name`` and ``default``.
        args: the positional arguments tuple received in the wrapper
        kwargs: the keyword arguments dict received in the wrapper
    
    Returns:
        tuple: 3 elements: the remaining args and the remaining kwargs
        after wrapper argument extraction and the separated wrapper kwargs
    """
    #create an empty dict for collecting wrapper keyword arguments
    wrapper_kwargs = dict()
    
    #separate the positional args for the wrapped function
    funcargs = args[:wrapped_argslen]
    
    #separation is needed, if arguments are defined for the wrapper
    if wrapper_args_def is not None:
        #separate the positional args for the wrapper
        wrapper_arg_vals = list(args[wrapped_argslen:])
        
        #loop on all wrapper argument names
        for wrapper_arg in wrapper_args_def:
            name = wrapper_arg['name']
            try:
                argval = wrapper_arg_vals.pop(0)
            except IndexError:
                if name in kwargs:
                    wrapper_kwargs[name] = kwargs[name]
                    del kwargs[name]
                elif 'default' in wrapper_arg:
                    wrapper_kwargs[name] = wrapper_arg['default']
                else:
                    raise TypeError("%s() missing keyword argument '%s'" % (wrapped.__name__, name))
            else:
                if name in kwargs:
                    raise TypeError("%s() got an unexpected keyword argument '%s'" % (wrapped.__name__, name))
                wrapper_kwargs[name] = argval
        else:
            #check whether any superflouos arguments were given
            if wrapper_arg_vals:
                expected_len = len(wrapper_args_def) + wrapped_argslen
                raise TypeError("%s() and decorator altogether take at most %d argument(s) (%d given)"
                                        % (
                                                wrapped.__name__,
                                                expected_len, 
                                                len(args), 
                                            )
                                    )
    
    #return the wrapper arguments and the remaining args and kwargs for wrapped
    return funcargs, kwargs, wrapper_kwargs


def _add_pattern_arguments(wrapped=None, wrapper_args_def=None):
    """Outer wrapper receiving the arguments for the wrapper
    
    This function is called when ``_add_pattern_arguments`` decorator is applied
    to a wrapped function either with or without arguments.
    
    When applied without arguments (and no brackets), ``wrapped`` is set to the
    wrapped function object and no ``wrapper_args_def``.
    
    If applied as ``@_add_pattern_arguments(wrapper_args_def=<>)``, no wrapped
    function object is given, only the ``wrapper_args_def``. In this case we
    record the ``wrapper_args_def`` and use functools to create partial object,
    which will be the replacement of the wrapped function.
    
    Args:
        wrapped (function object): the decorated function
        wrapper_args_def tuple): definition of list of arguments which are used by
            the wrapper only. Each such argument is defined by a dict with keys of
            ``name`` and ``default``.
    
    Note:
        @_add_pattern_arguments should use keyword arguments to be unambigous,
        as we have to figure out whether we were given the wrapped function or not.
        Well, if positional arguments are used and the first argument is not callable
        (i.e. not a function object (but the ``wrapper_args_def`` tuple), it is recognized.
    
    Returns:
        function object: the replacement (decorated) function
    """
    #when this function is called like @decorator_name(<arguments>). no wrapped function is given
    if not callable(wrapped):
        #create partial object, which will be the replacement of the wrapped function
        return functools.partial(_add_pattern_arguments, wrapper_args_def=wrapper_args_def)
    
    #get the wrapped function args length (minus the self, if any)
    #this has to suppose that the instance variable is called 'self', because
    #for some reason wrapped is a function here, not a method and
    #inspect.ismethod(wrapped) returns False :-(
    argslist = inspect.getargspec(wrapped).args
    wrapped_argslen = len(argslist)
    if argslist and argslist[0]=='self':
        wrapped_argslen -= 1
    
    @decorator
    def wrapper(wrapped, self, args, kwargs):
        """The decorator function that replaces the wrapped func
        
        Args:
            wrapped (function object): the decoreated reading function
            self (obj): the nbsr instance
            args: the positional arguments tuple for the decorated function
            kwargs: the keyword arguments dict for the decorated function
        
        Returns:
            any: whatever the reading function is to return
        """
        #first check whether worker thread still exists
        if self.workerthread is None:
            #simulate a standard reading function reaction on an attempt of reading a closed stream
            raise ValueError('I/O operation on closed file')
        
        #extract the arguments of the wrapper from all the arguments
        args, kwargs, wrapper_kwargs = _separate_args(
                                                                            wrapped,
                                                                            wrapped_argslen,
                                                                            wrapper_args_def,
                                                                            args, kwargs
                                                                        )
        
        #compile the patterns
        self._compile_patterns(**wrapper_kwargs)
        
        #call the wrapped reading function with the remaining arguments (self is sent by decorator)
        return wrapped(*args, **kwargs)
    
    return wrapper(wrapped)


class Mixin(object):
    """Mixin class for NonBlockingStreamReader, providing private methods"""
    #####
    ## class variables set dependent on Python 2 or 3
    #####
    #What type do we consider a pure pattern text (in contrast with compiled pattern)? Python 2: str & unicode; Python 3: str & bytes
    puretextpattern = (str, bytes) if sys.version_info[0]>2 else (str, unicode)
    #What class do we consider an re compiled pattern? From Python 3.7: re.Pattern; otherwise re._pattern_type
    re_pattern = re.Pattern if sys.version_info[0]>2 and sys.version_info[1]>6 else re._pattern_type
    #What ?????????
    
    def _populate_queue(self, stream):
        '''Collect data from 'stream' and put them in the 'queue'
        
        Worker function to be run as a child thread. It only reads 1 character at a time
        and put it into the queue. Where there is no more character to read, but there
        is no EOF yet (i.e. the stream source is stuck), this thread hangs.
        Reading only 1 character makes sure all data is read from the stream before
        it hangs. 
        
        Child thread cannot and must not raise exception, so if such is needed the 
        exception class is put into the queue, and the queue consumer is responsible
        to notice this and raise the exception of that class. The exception instance is
        also put into the queue as a 2nd element.
        
        Writing the self.EOF is thread-safe as this is the only place it is written, the
        parent only reads it.
        
        Args:
            stream (stream): the open stream where we read from
        '''
#        #by default there is no error instance
#        eInst = None
#        
        #loop on reading lines
        while True:
            try:
                #read 1 byte (type: str) and block until this byte can be read or stream gets closed
                queue_elem = stream.read(1)
                
            except ValueError as e:
#                eInst = e
#                #catch the exception when the stream became unexpectedly closed
#                if stream.closed:
#                    queue_elem = StreamUnexpectedlyClosed
#                else:
#                    #well, catch other ValueError exception too, even if we do not expect such
#                    queue_elem = e.__class__
                #catch the exception when the stream became unexpectedly closed
                if stream.closed:
                    queue_elem = StreamUnexpectedlyClosed(repr(e))
                else:
                    #well, catch other ValueError exceptions too, even if we do not expect such
                    queue_elem = e
            except Exception as e:
#                eInst = e
#                #actually, catch any non-terminating exception too, even if we have no idea what they are
#                queue_elem = e.__class__
                #put any non-terminating exception instance on the queue, even if we have no idea what they are
                queue_elem = e
            
            #put the character/byte (or empty string/bytes, if EOF), or exception instance into the queue
            self.linequeue.put(queue_elem)
#            
#            #check whether there was an excemption and the queue elem is a class
#            if eInst:
#                #also push the instance into the queue after the exception class
#                self.linequeue.put(eInst)
#                #no need for looping anymore, finish the worker
#                return
                
            #standard I/O read returns empty string/bytes on EOF
            if not len(queue_elem):
                #set the EOF flag
                self.EOF = True
                #finish the worker on EOF
                return
    
    
    def _readone(self, timeout=None):
        """Private function to read one character from the stream
        
        It is the consumer of the queue.
        
        If there is stream data in the queue, this functon returns it immediately.
        It returns empty string in case of EOF (same behaviour as regular read).
        If the queue is empty and no data can be read within the given timeout,
        the stream is stuck, so it raises the private _TimeOutOccured. The timeout
        can be explicitly provided in the argument or taken from the instance attribute. 
        
        Args:
            timeout (optional float): the timeout the reading max wait if the queue
                is empty. If missing or None, the atomic_timeout set earlier (in init or
                set_timeout) is used.
        
        Returns:
            str or bytes: 1 character/byte from the stream, or empty string/bytes on
                timeout or EOF
        
        Raises:
            _TimeOutOccured: no character arrived from the stream in the alotted time
            StreamUnexpectedlyClosed: the stream got closed while we were reading it
        """
        #first try to get the character from the buffer
        try:
            return self.bufferedchars.pop(0)
        except IndexError:
            pass
        
        #if there has been EOF already, there is no worker to populate the queue anymore, so just say EOF again
        if self.EOF:
            return b'' if self.is_binarystream else ''
        
        try:
            #get an element from the queue. Use the explicit timeout if exists, otherwise atomic
            queueelement = self.linequeue.get(
                                                            block=self.blockneeded,
                                                            timeout=timeout or self.atomic_timeout
                                                        )
        
        #Empty exception means that there was a timeout
        except queue.Empty:
            #raise exception
            raise _TimeOutOccured
        
        #if there was an error in the worker thread, it did put an instance of a descendant class of Exception into the queue
        if isinstance(queueelement, Exception):
#            #also get the exception instance from the queue (it must be there, i.e. can be blocking and no timeout)
#            eIsnt = self.linequeue.get()
#            #raise the exception with the values of the instance that the worker indicated
#            raise queueelement(eIsnt)
            #raise the exception that the worker indicated
            raise queueelement
            
        #if str, bytes or unicode was taken from the queue, just return it
        else:
            if self.debugprint:
                print(queueelement, end='', flush=True)
            return queueelement
    
    
    def _readbunch(self, size=None):
        """Private function to read a bunch of data from the stream defined at
        instance creation
        
        It tries to read as many data as possible until EOF, an end condition,
        or (on timeout) a matched pattern. An end condition can be the required
        number of bytes read for read(), or a new line caracter for readline(). It
        then returns whatever it could read.
        
        If reading ends for more than one reasons (i.e. pattern would match but
        there is EOF too), the precedence for returned reason is EOF first, then
        end condition and then pattern match. I.e. patterns are only checked
        (and pattern_index and match_object set), if there was some timeout and
        there is no other reason for finishing reading.
        However, if pattern check is still needed, do_pattern_check() can be used.
        
        If the return reason is a pattern match, the instance attributes of
        pattern_index and match_object are set (otherwise they are None).
        
        Args:
            size (int): the amount of data (number of bytes) to be read if
                it is a read(), or None for a readline()
        
        Returns:
            str or bytes: the read data if any, or empty string. Note that the return string
                does not indicate whether there was EOF or timeout. Such info can
                be retried from the returnby attribute.
        
        Raises:
            StreamUnexpectedlyClosed: the stream got closed while we were reading it
            or any exception that might have occured in the worker thread
        """
        #we are going to collect characters in the buffer (bytes or str, dependent on stream mode)
        buffer = b'' if self.is_binarystream else ''
        
        #indicate that no any pattern matched yet
        self.pattern_index = None
        self.match_object = None
        
        #the next timeout, whether atomic_timeout is to be used or long wait (None=atomic)
        this_timeout = None
        
        #create a counter if it is a read()
        if size is not None:
            cnt = 0
        
        #loop on reading characters until an end condition or EOF is found, or timeout
        while True:
            try:
                #read 1 character with atomic_timeout for 1st read, or timeout after that
                ch = self._readone(this_timeout)
            
            except _TimeOutOccured:
                #this_timeout=None indicate that this was an atomic timeout
                if this_timeout is None:
                    #progress to pattern search (after the else clause)
                    pass
                else:
                    #if long timeout occured, return the content of the buffer (can be empty)
                    self.returnby = returnby_TIMEOUT
                    return buffer
            
            except Exception:
                #if the stream became closed, or any other exception, let the exception escalate to the caller
                raise
            
            #successful read
            else:
                #the previous read might have had long timeout, so reset it now to atomic timeout after a successful read
                this_timeout = None
                
                #add the character (or empty string in case of EOF) to the buffer
                buffer += ch
                
                #check whether EOF occured
                if not len(ch):
                    #return the buffer at EOF
                    self.returnby = returnby_EOF 
                    return buffer
                
                #there is no size for readline() and readlines()
                if size is None:
                    if ch == '\n' or ch == b'\n':
                        #if it is at the end of a line, return the line (can be an empty line)
                        self.returnby = returnby_NEWLINE
                        return buffer
                
                #size is set for read()
                else:
                    #increment the counter
                    cnt += 1
                    #if reached the desired amount, return
                    if cnt >= size:
                        #we have read enough, return the buffer
                        self.returnby = returnby_SIZE
                        return buffer
                        
                #read on
                continue
                
            #as atomic timeout happened, check patterns whether any of them matches
            if self.do_pattern_check(buffer):
                #set the return reason and return the buffer
                self.returnby = returnby_PATTERN
                return buffer
            
            #set a longer timeout for the next read and continue reading attempt
            this_timeout = self.timeout_diff
            continue
        
    
    def _compile_patterns(self, expected_patterns=None, regexflags=0):
        """Private function to compile re patterns
        
        It checks whether the patters in the list need to be compiled and if so,
        compile them and store them in an instance attribute.
        
        Args:
            expected_patterns (optional tuple/list): a list of patterns that we wait for.
                If any of these patterns match, we return immediately, not waiting
                for EOF or timeout. List elements (the patterns) can be pure text or
                re compiled.
            regexflags (optional int): see the re module, e.g. re.IGNORECASE. Or
                re.VERBOSE meaning white space is not part of the pattern (unless
                escaped) and comments can appear. Note that if expected_patterns
                element is already compiled, these flags here are ignored.
        
        Raises:
            rePatternError: One of the expected patterns cannot compile
        """
        #collect compiled patterns is a loop
        self.compiled_patterns = []
        
        #if there is no expacted pattern list (None or empty list), do nothing
        if not expected_patterns:
            return
        
        #sanity check of the expected pattern list
        if not isinstance(expected_patterns, (list, tuple)):
            raise ValueError(
                'expected_patterns should be either a list or tuple, '
                'but it is %s'%type(expected_patterns)
            )
        
        #loop on all received pattern
        for expected_pattern in expected_patterns:
            #already compiled?
            if isinstance(expected_pattern, self.re_pattern):
                #figure out they type of the pattern that was compiled
                pattern_type_binary = isinstance(expected_pattern.pattern, bytes)
                
                #indicate that the pattern is already compiled
                alreadycompiled = True
            
            #pure text pattern (text can be bytes too)?
            elif isinstance(expected_pattern, self.puretextpattern):
                #figure out they type of the pattern
                pattern_type_binary = isinstance(expected_pattern, bytes)
                
                #indicate that the pattern is already compiled
                alreadycompiled = False
            
            #unrecognised pattern type?
            else:
                raise ValueError(
                    'The expected pattern %s can only be a string/bytes, '
                    'or an already compiled re pattern, '
                    'but %s found'%(repr(expected_pattern), type(expected_pattern))
                )
            
            #XOR the stream and the pattern type (yields True when they do not match)
            if self.is_binarystream ^ pattern_type_binary:
                if self.is_binarystream:
                    raise ValueError(
                        'A binary stream cannot be searched for with a non-binary pattern '
                        '%s'%(repr(expected_pattern))
                    )
                else:
                    raise ValueError(
                        'A non-binary (text) stream cannot be searched for with a binary pattern '
                        '%s'%(repr(expected_pattern))
                    )
            
            if alreadycompiled:
                #just append the compiled re pattern into the list
                self.compiled_patterns.append(expected_pattern)
                
            else:
                try:
                    #compile the pattern and append it to the list
                    self.compiled_patterns.append(
                                                                re.compile(
                                                                                expected_pattern,
                                                                                regexflags
                                                                            )
                                                            )
                
                except Exception as e:
                    raise rePatternError(
                        'compile error in pattern %s:%s'%(
                            repr(expected_pattern),
                            str(e)
                        )
                    )
