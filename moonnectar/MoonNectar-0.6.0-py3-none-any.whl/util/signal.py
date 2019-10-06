"""
Qt style signals/slots implementation with optional PyQt5 event loop integration.

Signals and Slots are a programming construct introduced by Qt in order to communicate
between objects using a simple observer pattern.

https://en.wikipedia.org/wiki/Signals_and_slots

This module implements a signal/slot capability which can either be run on its own (no
Qt installation) or via the Qt event loop.  The interface mimics the `pyqtSignal`
construct of PyQt5.
"""

import logging

_logger = logging.getLogger(__name__)

import abc
import asyncio
import collections
import functools
import inspect
import weakref

from enum import Enum
from functools import singledispatch, update_wrapper
from threading import Lock

from .decorator import Decorator

try:
    from PyQt5 import QtCore
except ImportError: # pragma: no cover
    QtCore = None


def singledispatchmethod(func): # pragma: no cover
    dispatcher = singledispatch(func)

    def wrapper(*args, **kw):
        return dispatcher.dispatch(args[1].__class__)(*args, **kw)

    wrapper.register = dispatcher.register
    update_wrapper(wrapper, func)
    return wrapper

SlotKey = collections.namedtuple(
    "SlotKey", ("id", "repr", "signal"), defaults = (False,)
)

class DispatchDirect:
    """
    Context aware function execution:  Direct Function Call

    Executes all functions as an immediate function call in the current thread
    """
    def execute(self, func, *arg):
        func(*arg)
        return True

if QtCore:
    class DispatchQtApp:
        """
        Context aware function execution:  Qt Application Event Loop

        Executes all functions via the Qt Application's event loop.  This is occurs by
        creating a new Qt object which is moved into the application thread.  The new
        object has a signal which is called which executes the provided function as part
        of the event loop.
        """

        class QSigRunner(QtCore.QObject):
            sig_run = QtCore.pyqtSignal(object, tuple)

            def __init__(self, *arg, **kw):
                super().__init__(*arg, **kw)

            def on_sig_run(self, func, args):
                func(*args)

            # NOTE:  Signals must be connected AFTER moving an object to a new thread
            # ...    As this object is always has a call to move to a different thread
            #        and always has a signal connected, a custom moveToThread function
            #        is used which creates the signal after moving the object to a new
            #        thread.  Best guess (2019/07/04) is that this indicates connected
            #        signals are thread aware.
            #
            # NOTE:  An alternative which seems to work is to declare the slot
            #        explicitly using ``pyqtSlot(...)``.  Best guess (2019/07/040 is
            #        that this indicates that python methods (without a pyqtSlot
            #        declaration) are stored differently than C++ signals (pyqtSlot
            #        declares the C++ signal).
            #
            def moveToThread(self, *arg, **kw):
                super().moveToThread(*arg, **kw)
                self.sig_run.connect(self.on_sig_run)

        def setup(self):
            """
            Setup the Qt function executer object if it does not yet exist.
            """
            if QtCore and not hasattr(self, 'qt_sig_runner') or self.qt_sig_runner is None:
                app = QtCore.QCoreApplication.instance()
                if app:
                    self.qt_sig_runner = self.QSigRunner()
                    self.qt_sig_runner.moveToThread(app.thread())
                    self.qt_sig_runner.setParent(app)
                else:
                    self.qt_sig_runner = None

        def execute(self, func, *arg):
            self.setup()
            if self.qt_sig_runner:
                self.qt_sig_runner.sig_run.emit(func, arg)
                return True
            else:
                return False

class BoundSignal:
    DISPATCHERS = {
        'direct': DispatchDirect,
    }

    if QtCore:
        DISPATCHERS['qt-app'] = DispatchQtApp

    def __init__(self, signal, name, dispatchers, instance, owner, log_emit=True):
        self._signal    = weakref.ref(signal)
        self._name      = name
        self._instance  = weakref.ref(instance, self._on_signal_death)
        self._owner     = owner
        self._slot_attr = f"_{self._name}_{self.__class__.__name__}_slots"
        self._disp_attr = f"_{self._name}_{self.__class__.__name__}_disp"
        self._alive     = True
        self._log_emit  = log_emit

        # Verify the instance has a slots container
        if not hasattr(instance, self._slot_attr):
            setattr(instance, self._slot_attr, dict())

        # Verify the instance has dispatchers configured
        if not hasattr(instance, self._disp_attr):
            dispatch_objs = []
            for key in dispatchers:
                if key not in self.DISPATCHERS:
                    raise ValueError(f"Invalid Slot Dispatcher Type: `{key}`")
                else:
                    dispatch_objs.append(self.DISPATCHERS[key]())

            setattr(instance, self._disp_attr, dispatch_objs)

    def _on_signal_death(self, ref):
        self._alive = False

    @property
    def _slots(self):
        return getattr(self._instance(), self._slot_attr, None)

    @property
    def _dispatchers(self):
        return getattr(self._instance(), self._disp_attr, [])

    def __repr__(self):
        if self._alive:
            return f"<Bound Signal '{self._name}' of {self._owner.__name__} at {hex(id(self._instance()))}>"
        else:
            return f"<Bound Signal '{self._name}' of {self._owner.__name__} at [dead]>"

    def _get_keyref(self, slot):

        # Get a key and reference for a specified slot
        # ... Prefer a weak reference when possible
        # ... However, some callable objects are not weak referenceable
        # ... In particular, `pyqtBoundSignal` objects and their `emit` signals

        if isinstance(slot, BoundSignal):
            key = SlotKey(id(slot), repr(slot.emit), True)
            ref = weakref.WeakMethod(slot.emit, lambda wref: self.disconnect(key))

        elif inspect.ismethod(slot) and isinstance(slot.__self__, BoundSignal):
            key = SlotKey(id(slot.__self__), repr(slot), True)
            ref = weakref.WeakMethod(slot, lambda wref: self.disconnect(key))

        elif QtCore and isinstance(slot, QtCore.pyqtBoundSignal):
            ref = slot.emit
            key = SlotKey(id(slot), repr(slot.emit), True)

        elif (
            QtCore
            and hasattr(slot, '__self__')
            and isinstance(slot.__self__, QtCore.pyqtBoundSignal)
        ):
            # pyqtBoundSignal and its methods cannot be weakref
            ref = slot
            key = SlotKey(id(slot.__self__), repr(slot), True)

        elif inspect.ismethod(slot):
            key = SlotKey(id(slot.__self__), repr(slot), False)
            ref = weakref.WeakMethod(slot, lambda wref: self.disconnect(key))

        elif callable(slot):
            key = SlotKey(id(slot), repr(slot), False)
            ref = weakref.ref(slot, lambda wref: self.disconnect(key))

        else:
            raise TypeError(f"{self!r}: Invalid Slot Type: {slot}")

        return (key, ref)

    def connect(self, slot):
        if self._alive:
            key, ref = self._get_keyref(slot)

            _logger.debug3(
                f"Connect {self._owner.__name__}"
                f"[@{hex(id(self._instance))}]"
                f".{self._name}"
                f" to slot: {key.repr}"
            )

            self._slots[key] = ref
            return key

    def disconnect(self, slot):
        if self._alive:
            if isinstance(slot, SlotKey):
                key = slot
            else:
                try:
                    key, ref = self._get_keyref(slot)
                except TypeError:
                    return False

            if key in self._slots:
                _logger.debug3(
                    f"Disconnect {self._owner.__name__}"
                    f"[@{hex(id(self._instance))}]"
                    f".{self._name}"
                    f" from slot: {key.repr}"
                )
                self._slots.pop(key)
                return True
            else:
                return False
        else:
            # Implicit success by virtue of signal deletion
            return True

    def connected(self, slot):
        if self._alive:
            if isinstance(slot, SlotKey):
                key = slot
            else:
                try:
                    key, ref = self._get_keyref(slot)
                except TypeError:
                    return False

            if key in self._slots:
                return True
            else:
                return False
        else:
            # Implicit disconnect happend because of signal deletion
            return False

    def emit(self, *arg):
        # Signal Dispatch Priority
        # ========================
        # DEF 'Dispatch': The thread where a slot is executed
        #
        # - Available Dispatch Methods:
        #   - Direct execution:
        #     - Executed by the emit method (in the emitting thread)
        #     - All Signal and pyqtBoundSignal objects are always direct execution
        #     - Because they will each have their own dispatch mechanisms
        #   - Qt Application Event Loop:
        #     - Executed within the context of the Qt Application Event Loop
        #     - This can be obtained automatically at any time
        #     - This ensures a random signal is safe for Qt actions
        #     - Useful for single-threaded Qt applications
        #   - Qt Event Loop:
        #     - A Qt event loop specified by the user
        #     - This is for multi-threaded Qt applications
        #     - Correct event loop may be detected via Qt thread afinity
        #       - QtCore.QThread.currentThread()
        #     - User may specify a different thread (event loop) for execution
        #   - Asyncio Event Loop:
        #     - If Qt is not available
        #     - Permits execution of a slot in a different thread
        #     - Permits slots to be executed as asyncio tasks
        #       - slot code plays nice with other async tasks
        #     - May be in the current thread (automatic)
        #     - May be in a different thread (user supplied loop)
        #     - Slots are run by creating a new asyncio task for each slot
        #
        # - Dispatch Location Determination:
        #   - Determined by the signal:
        #     - Default: qt-auto, asynci-auto, direct
        #     - User may override per signal instance
        #   - Determined by connection:
        #     - Default: signal default
        #     - User may override in the ``connect`` method


        # Iterate over a copy of connected slots instead of the real list
        # ... This permits connected slots to perform connect and disconnect operations
        #     while still iterating over the list with no threading problems.
        alive = self._slots.copy()
        dead = []
        for key, ref in alive.items():
            if self._log_emit:
                curframe = inspect.currentframe()
                caller   = inspect.getouterframes(curframe)[1]
                _logger.log(
                    self._log_emit,
                    f"Emit {self._owner.__name__}"
                    f"[@{hex(id(self._instance))}]"
                    f".{self._name}"
                    f" to slot: {key.repr}"
                    f"\nfrom {caller.function}"
                    f"\nfile {caller.filename}"
                    f" @{caller.lineno}"
                )
            # For any signal object, just call the emit method
            # ... the called signal can handle any special dispatching
            if key.signal:
                try:
                    if isinstance(ref, weakref.ref):
                        ref()(*arg)
                    else:
                        ref(*arg)
                except Exception as ex: # pragma: no cover
                    # On any exception, assume this indicates a dead object
                    # No interesting test case has been identified
                    # ... but still included in case the situation occurs
                    # ... PyQt5 can generate such an exception when calling a deleted signal
                    # ... however, it sometimes causes a segfault instead
                    _logger.debug2("Exception in callback, assuming a dead signal source object",
                                  exc_info = True)
                    dead.append(key)

            else:
                executed = False

                cb = ref()
                for dispatch in self._dispatchers:
                    if dispatch.execute(cb, *arg):
                        executed = True
                        break

                if not executed:
                    _logger.error(f"Signal {self!r} all dispatchers failed to execute slot {key}")


        # Remove any signals that failed to execute
        for key in dead: # pragma: no cover
            self.disconnect(key)


class Signal:
    DEFAULT_DISPATCH = ['qt-app', 'direct']

    def __set_name__(self, owner, name):
        self._name = name
        self._slot_inst = f"_{self._name}_{BoundSignal.__name__}_instance"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.bind(instance, owner)

    def bind(self, instance, owner):
        # Create a persistent bound signal instance
        # ... This both speeds up signal processing by eliminating class initialization
        # ... Also permits BoundSignal instances and methods to be weak referenceable
        if not hasattr(instance, self._slot_inst):
            setattr(
                instance,
                self._slot_inst,
                BoundSignal(self, self._name, self._dispatch, instance, owner, self._log_emit)
            )
        return getattr(instance, self._slot_inst)

    def __init__(self, dispatch = DEFAULT_DISPATCH, *, log=logging.DEBUG2):
        """
        :param dispatch: The context where connected slots will be executed
        :param log: The level at which emit messages should be logged
        """

        if type(dispatch) == str:
            self._dispatch = (dispatch,)
        else:
            self._dispatch = tuple(dispatch)

        self._log_emit = log

    @staticmethod
    def autoconnect(cls):
        """
        Class decorator for automatically connecting instance methods to signals
        """
        old_init = cls.__init__

        @functools.wraps(old_init)
        def new_init(self, *args, **kwargs):
            for name, method in inspect.getmembers(
                self,
                predicate = lambda _: (inspect.ismethod(_) and hasattr(_, "_signals")),
            ):
                for sig in method._signals:
                    bound = getattr(self, sig._name)
                    bound.connect(method)

            old_init(self, *args, **kwargs)

        cls.__init__ = new_init
        return cls

    def connect(self, func):
        """
        Method Decorator used to mark a method as a slot for signal auto connection
        """

        if not hasattr(func, '_signals'):
            func._signals = set()

        func._signals.add(self)

        return func

class call_via_signal(Decorator):
    """
    Call the wrapped method or function via a signal instead of direct call.
    Note that return values will be ignored!
    """
    __call_signal = Signal()

    def __init__(self, func=None):
        super().__init__(func)

        self.__call_signal.connect(self.__signal_callback)

    def _call_wrapped(self, *args, **kwargs):
        self.__call_signal.emit(args, kwargs)

    def __signal_callback(self, args, kwargs):
        rv = super()._call_wrapped(*args, **kwargs)
