import logging
import watchdog
import watchdog.events
import watchdog.observers

from mnectar.config   import Configurable

import Registry.Library

_logger = logging.getLogger('mnectar.'+__name__)

class LibraryWatchdogEventHandler(watchdog.events.FileSystemEventHandler):
    def __init__(self, app=None, *arg, **kw):
        super().__init__(*arg, **kw)
        self.app = app

    def on_created(self, event):
        super().on_created(event)

        try:
            if event.is_directory:
                _logger.debug3(f"Directory Created (no action): {event.src_path}")
            else:
                _logger.debug2(f"New File Detected: {event.src_path}")
                self.app.library.scanFile(event.src_path)
        except Exception as ex:
            _logger.exception(f"Exception in watchdog event: {ex}")

    def on_deleted(self, event):
        super().on_deleted(event)

        try:
            if event.is_directory:
                _logger.debug3(f"Directory Deleted (no action): {event.src_path}")
            else:
                self.app.library.deleteFile(event.src_path)
        except Exception as ex:
            _logger.exception(f"Exception in watchdog event: {ex}")

    def on_modified(self, event):
        super().on_modified(event)

        try:
            if event.is_directory:
                _logger.debug3(f"Directory Modified (no action): {event.src_path}")
            else:
                _logger.debug2(f"File Modified: {event.src_path}")
                self.app.library.scanFile(event.src_path)
        except Exception as ex:
            _logger.exception(f"Exception in watchdog event: {ex}")

    def on_moved(self, event):
        super().on_moved(event)

        try:
            if event.is_directory:
                _logger.debug3(f"Directory Moved (no action): [{event.src_path}] => [{event.dest_path}]")
            else:
                self.app.library.moveFile(event.src_path, event.dest_path)
        except Exception as ex:
            _logger.exception(f"Exception in watchdog event: {ex}")

class LibraryWatchdog(Registry.Plugin, Configurable, registry=Registry.Library.Extensions):
    observer = None

    @classmethod
    def create_config(cls, parser):
        parser.add_argument('--plugin-watchdog-enable', action = 'store_true', help = "Enable the watchdog plugin")

    def enable(self):
        if self.app.config.plugin_watchdog_enable and self.observer is None:
            self.event_handler = LibraryWatchdogEventHandler(self.app)
            self.observer      = watchdog.observers.Observer()
            self.watchers      = {}

            self.observer.start()

            self.app.library.libraryDirAdded  .connect(self.on_library_dir_added)
            self.app.library.libraryDirRemoved.connect(self.on_library_dir_added)

            for path in self.app.library.directories:
                self.on_library_dir_added(path)

            _logger.debug(f"Library Watchdog Running")

    def disable(self):
        self.app.library.libraryDirAdded  .disconnect(self.on_library_dir_added)
        self.app.library.libraryDirRemoved.disconnect(self.on_library_dir_added)
        self.observer.stop()
        self.observer = None

        _logger.debug(f"Library Watchdog Stopped")

    def on_library_dir_added(self, path):
        if not path in self.watchers:
            self.watchers[path] = self.observer.schedule(self.event_handler, path, recursive=True)
            _logger.debug(f"New Library Watchdog: {path}")

    def on_library_dir_removed(self, path):
        if path in self.watchers:
            self.observer.unschedule(self.watchers.pop(path))
            _logger.debug(f"Library Watchdog Removed: {path}")
