# MacOS Multimedia Key Connection
#
# This code was inspired in part by:
#   Quod Libet music player
#   osxmmkeys python library

import logging
import time

from mnectar.registry       import Plugin, Registry
from mnectar.registry       import PluginSetting
from mnectar.util.signal    import Signal
from mnectar.util.decorator import oscheck

_logger = logging.getLogger(__name__)

try:
    import AppKit
    import Quartz
    import threading

    class MacSpecialKeyEventTap(threading.Thread):
        """
        MacOS Multimedia Key Event Handler
        ----------------------------------

        MacOS does not make it easy to access keyboard multimedia keys.
        In order to gain to these specal keys, Cocoa/Quartz routines must be used
        to tap into the system event handler, which is not available in GUI
        toolkits.  PyObjC provides the necesary access to system routines.
        """

        keyPlayNext  = Signal()
        keyPlayPause = Signal()
        keyPlayPrev  = Signal()

        MEDIA_EVENT_SUBTYPE = 8

        def __init__(self, *arg, **kw):
            super().__init__(*arg, **kw)

            # Event Key Codes:
            #   16: Play / Pause
            #   17: Next Track
            #   18: Previous Track
            #   19: Next Track
            #   20: Previous Track

            self._handlers = {
                    16: self.keyPlayPause.emit,
                    17: self.keyPlayNext.emit,
                    18: self.keyPlayPrev.emit,
                    19: self.keyPlayNext.emit,
                    20: self.keyPlayPrev.emit}

            self.initEvent = threading.Event()

        def _loop_start(self, observer, activiti, info):
            self.initEvent.set()

        def run(self):
            # Create the tap
            self._tap = Quartz.CGEventTapCreate(
                    Quartz.kCGSessionEventTap,
                    Quartz.kCGHeadInsertEventTap,
                    Quartz.kCGEventTapOptionDefault,
                    Quartz.CGEventMaskBit(AppKit.NSSystemDefined),
                    self._handle_event_tap,
                    None)

            # the above can fail
            if self._tap is None: #pragma: no cover
                # Not testable, but necessary in case of fringe case failures
                self.initEvent.set()
                return

            # Get the run loop
            self._loop = Quartz.CFRunLoopGetCurrent()

            # add an observer so we know when we can stop it
            # without a race condition
            self._observ = Quartz.CFRunLoopObserverCreate(
                None, Quartz.kCFRunLoopEntry, False, 0, self._loop_start, None)

            Quartz.CFRunLoopAddObserver(
                self._loop, self._observ, Quartz.kCFRunLoopCommonModes)

            # Create the run loop source
            self._run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, self._tap, 0)

            Quartz.CFRunLoopAddSource(
                    self._loop,
                    self._run_loop_source,
                    Quartz.kCFRunLoopDefaultMode)

            #XXX Necessary?  Not in Quod Libet
            Quartz.CFRetain(self._loop)

            Quartz.CGEventTapEnable(self._tap, True)
            Quartz.CFRunLoopRun()  # Only returns after stop() is called.

        def event_loop_ready(self):
            return Quartz.CFRunLoopIsWaiting(self._loop)

        def stop(self):
            # wait until we fail or the observer tells us that the loop has started
            self.initEvent.wait()

            # remove the runloop source
            Quartz.CFRunLoopRemoveSource(
                self._loop,
                self._run_loop_source,
                Quartz.kCFRunLoopDefaultMode
            )
            self._run_loop_source = None

            # remove observer
            Quartz.CFRunLoopRemoveObserver(
                self._loop, self._observ, Quartz.kCFRunLoopCommonModes)
            self._observ = None

            # stop the loop
            Quartz.CFRunLoopStop(self._loop)
            Quartz.CFRelease(self._loop)
            self._loop = None

            # Disable the tap
            Quartz.CGEventTapEnable(self._tap, False)
            self._tap = None

        def _handle_event_tap(self, proxy, cg_event_type, cg_event, refcon): # pragma: no cover
            # NOTE: Tested manually as no easy automated solution was found
            ns_event = AppKit.NSEvent.eventWithCGEvent_(cg_event)

            # event Trap disabled by timeout or user input, re-enable
            if cg_event_type == Quartz.kCGEventTapDisabledByUserInput or \
                    cg_event_type == Quartz.kCGEventTapDisabledByTimeout:
                assert self._tap is not None
                Quartz.CGEventTapEnable(self._tap, True)
                return cg_event


            if not self._handle_event(ns_event):
                return cg_event  # Allow event to propagate.

        def _handle_event(self, event):

            if event.subtype() != self.MEDIA_EVENT_SUBTYPE:
                return False

            data  = event.data1()
            code  = (data & 0xFFFF0000) >> 16
            state = (data & 0xFF00) >> 8

            if state != AppKit.NSKeyDown or code not in self._handlers:
                return False

            if self._handlers[code] is not None:
                self._handlers[code]()
                return True

except ImportError as ex: # pragma: no cover
    _logger.debug3("MacOS Multimedia Keys are Not Available!")

class MacMMKeyPlugin(Plugin, registry=Registry.Control):
    enabled = PluginSetting(default=True)

    @property
    def running(self):
        return hasattr(self, '_tap') and self._tap.event_loop_ready()

    @oscheck(target="Darwin")
    def enable(self, retry=1):
        retry_count = 0
        while retry_count < retry:
            if not hasattr(self, '_tap'):
                if retry_count > 0: # pragma: no cover
                    # In rare cases startup fails the first time (mostly during testing)
                    # ... but not reliably ...
                    time.sleep(0.1)
                    _logger.debug(f"MacOS Multimedia Key Tap Starting [Retry #{retry_count}] ...")
                else:
                    _logger.debug(f"MacOS Multimedia Key Tap Starting ...")

                # Create the key tap
                self._tap = MacSpecialKeyEventTap(daemon = True)

                # Start the key tap thread
                self._tap.start()

                # Wait for tap initialization to complete
                # .. this ensures calling code knows the tap is ready for use immediately
                self._tap.initEvent.wait()

                if self._tap.event_loop_ready():
                    # Connect relevant signals
                    self._tap.keyPlayNext .connect(self.app.signal.mmkey_playNext   .emit)
                    self._tap.keyPlayPrev .connect(self.app.signal.mmkey_playPrev   .emit)
                    self._tap.keyPlayPause.connect(self.app.signal.mmkey_togglePause.emit)
                    return True
                else: # pragma: no cover
                    _logger.error("MacOS Multimedia Key Tap Startup Failed!")
                    self._tap.stop()
                    del self._tap
            retry_count += 1

    @oscheck(target="Darwin")
    def disable(self):
        if hasattr(self, '_tap'):
            _logger.debug(f"MacOS Multimedia Key Tap Stopping ...")

            # Wait for tap initialization to complete
            # ... This guards against potential threading issues
            self._tap.initEvent.wait()

            # Disconnect all signals
            self._tap.keyPlayNext .disconnect(self.app.signal.mmkey_playNext   .emit)
            self._tap.keyPlayPrev .disconnect(self.app.signal.mmkey_playPrev   .emit)
            self._tap.keyPlayPause.disconnect(self.app.signal.mmkey_togglePause.emit)

            # Stop the key tap & thread
            self._tap.stop()

            # Join the thread until it completes
            # ... this ensures shutdown completes before any other action occurs
            self._tap.join()

            # Delete the tap object
            # ... which also indicates the tap is not running
            del self._tap

