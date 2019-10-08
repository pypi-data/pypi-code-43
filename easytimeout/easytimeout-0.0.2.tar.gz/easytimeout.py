#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import functools
from threading import Event, Thread


__all__ = [ 'Timeout' ]

if not hasattr(__builtins__, 'TmeoutError'):
    class TimeoutError(RuntimeError):
        def __init__(self, *args, **kwargs):
            super(TimeoutError, self).__init__(*args, **kwargs)


class Timeout(object):
    def __init__(self, limit, timeout_result=None):
        """Add time limit to excution of your function
        
        Arguments:
            limit {int} -- if the execution of your function has exceeded the time limit in seconds, it will be interrupted.
        
        Keyword Arguments:
            timeout_result {callable or any} -- If timeout_result is a callable, it will be called with all the parameters were passed to 
            your function while your function timeout, and its return value willed be taken as your function's return value, otherwise,
            if timeout_result will be taken as your function's return value. The TimeoutError will be raise if timeout_result is None. (default: {None})
        """
        
        self._limit_ = limit
        self.__timeout_result__ = timeout_result

    def __set_result__(self, result, exception, event):
        def wrapper(result_value, exception_value):
            result.append(result_value)
            exception.append(exception_value)
            event.set()
        return wrapper

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result, exception = [], []
            event = Event()
            execution_thread = ExecutionThread(func, args=args, kwargs=kwargs, callback=self.__set_result__(result, exception, event))
            execution_thread.start()
            if event.wait(self._limit_):
                if exception and exception[0] is not None:
                    raise exception[0]
                return result[0]
            else:
                execution_thread.terminate()
                if callable(self.__timeout_result__):
                    return self.__timeout_result__(*args, **kwargs)
                elif self.__timeout_result__ is not None:
                    return self.__timeout_result__
                raise TimeoutError('{} exceeded time limit'.format(func.__name__))
        return wrapper

    
class ExecutionThread(Thread):
    def __init__(self, func, args=(), kwargs={}, callback=None):
        super(ExecutionThread, self).__init__()
        self.daemon = True
        self._func_ = func
        self._args_ = args
        self._kwargs_ = kwargs
        self.__callback__ = callback
        self.__event__ = Event()

    def terminate(self):
        self.__event__.set()

    def __execute__(self):
        res, exception = None, None
        try:
            res = self._func_(*self._args_, **self._kwargs_)
        except Exception as e:
            exception = e
        self.__callback__(res, exception)
        self.terminate()

    def run(self):
        _exec_thread_ = Thread(target=self.__execute__)
        _exec_thread_.daemon = True
        _exec_thread_.start()
        self.__event__.wait()
    
