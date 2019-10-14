#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base callbackManager class
"""

from __future__ import print_function, division, absolute_import

import sys

import tpDccLib
from tpDccLib.abstract import callback


class CallbacksManager(object):
    """
    Static class used to manage all callbacks instances
    """

    _initialized = False

    @classmethod
    def initialize(cls):
        """
        Initializes all module callbacks
        """

        if cls._initialized:
            return

        default_callbacks = {
            'Tick': callback.PythonTickCallback
        }

        try:
            shutdown_type = getattr(tpDccLib.Callbacks, 'ShutdownCallback')
        except AttributeError:
            shutdown_type = None

        for callback_name in tpDccLib.callbacks():

            # Get callback type from tpDccLib.DccCallbacks
            n_type = getattr(tpDccLib.DccCallbacks, callback_name)[1]['type']
            if n_type == 'simple':
                callback_type = callback.SimpleCallback
            elif n_type == 'filter':
                callback_type = callback.FilterCallback
            else:
                tpDccLib.logger.warning('Callback Type "{}" is not valid! Using Simplecallback instead ...'.format(n_type))
                callback_type = callback.SimpleCallback

            # We extract callback types from the specific registered callbacks module
            if not hasattr(tpDccLib, 'Callbacks'):
                tpDccLib.logger.warning('DCC {} does not Callbacks registered!'.format(tpDccLib.Dcc.get_name()))
                return

            callback_class = getattr(tpDccLib.Callbacks, '{}Callback'.format(callback_name), None)
            if not callback_class:
                callback_class = default_callbacks.get(callback_name, callback.ICallback)
                tpDccLib.logger.warning('Dcc {} does not provides an ICallback for {}Callback. Using {} instead'.format(tpDccLib.Dcc.get_name(), callback_name, callback_class.__name__))

            new_callback = getattr(tpDccLib, callback_name, None)
            if new_callback:
                new_callback.cleanup()
            tpDccLib.register_class(callback_name, callback_type(callback_class, shutdown_type))

            tpDccLib.logger.debug('Creating Callback "{}" of type "{}" ...'.format(callback_name, callback_class))

        cls._initialized = True

    @classmethod
    def register(cls, callback_type, fn, owner=None):
        """
        Registers, is callback exists, a new callback
        :param callback_type: str, type of callback
        :param fn: Python function to be called when callback is emitted
        :param owner, class
        """

        if type(callback_type) in [list, tuple]:
            callback_type = callback_type[0]

        if callback_type in sys.modules[tpDccLib.__name__].__dict__.keys():
            sys.modules[tpDccLib.__name__].__dict__[callback_type].register(fn, owner)

    @classmethod
    def unregister(cls, callback_type, fn):
        """
        Unregisters, is callback exists, a new callback
        :param callback_type: str, type of callback
        :param fn: Python function we want to unregister
        """

        if type(callback_type) in [list, tuple]:
            callback_type = callback_type[0]

        if callback_type in sys.modules[tpDccLib.__name__].__dict__.keys():
            sys.modules[tpDccLib.__name__].__dict__[callback_type].unregister(fn)

    @classmethod
    def unregister_owner_callbacks(cls, owner):
        """
        Unregister all the callbacks from all registered callbacks that belongs to a specific owner
        :param owner: class
        """

        if not cls._initialized:
            return

        for k, v in sys.modules[tpDccLib.__name__].__dict__.items():
            if isinstance(v, callback.AbstractCallback):
                v.unregister_owner_callbacks(owner=owner)

    @classmethod
    def cleanup(cls):
        """
        Cleanup all module callbacks
        :param owner: class, If given, only
        :return:
        """

        if not cls._initialized:
            return

        for k, v in sys.modules[tpDccLib.__name__].__dict__.items():
            if isinstance(v, callback.AbstractCallback):
                v.cleanup()

        cls._initialized = False
