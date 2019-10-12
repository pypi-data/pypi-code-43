import os
import time
import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

__all__ = ['EventHandler', 'WatchDog']


class EventHandler(FileSystemEventHandler):
    """
    Inherits from watchdog.events.FileSystemEventHandler.
    Overrides the on_modified event
    to call the callback specified in the constructor
    if any file matching the patterns specified is
    modified.

    You can subclass the class for your own needs and override other methods.

    @param: callback: The function to call when any tracked file is modified
    @param: include_files: A list of `absolute file names` to track for modification.
    @param: exclude_files: A list of files to ignore tracking.
    @param: include_patterns: A list of unix style file patterns to match files
    to track(Uses fnmatch.fnmatch(filename, pattern))
    Same applies to exclude patterns.
    """

    def __init__(self, callback, include_files=None, exclude_files=None,
                 include_patterns=None, exclude_patterns=None,
                 verbose=False):

        self.callback = callback
        self.include_files = include_files
        self.exclude_files = exclude_files
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
        self.verbose = verbose

        self.time = time.time()

    def is_ignored_file(self, filename):
        """
        Returns True if filename is in excluded_files else False
        If excluded files is None, It returns False
        """

        if self.exclude_files is None:
            return False
        if filename in [os.path.expanduser(p) for p in self.exclude_files]:
            return True
        return False

    def is_ignored_pattern(self, filename):
        """
        Returns True if filename matches any pattern in exclude_patterns.
        If exclude_patterns is None, It returns False
        """

        if self.exclude_patterns is None:
            return False

        for pat in self.exclude_patterns:
            if fnmatch.fnmatch(filename, pat):
                return True
        return False

    def is_included_file(self, filename):
        """
        Returns True if filename is in include_files else False
        If  include_files is None, It returns False
        """
        if self.include_files is None:
            return False
        if filename in [os.path.expanduser(p) for p in self.include_files]:
            return True
        return False

    def is_included_pattern(self, filename):
        """
        Returns True if filename matches any pattern in include_patterns.
        If include_patterns is None, It returns False
        """

        if self.include_patterns is None:
            return False

        for pat in self.include_patterns:
            if fnmatch.fnmatch(filename, pat):
                return True
        return False

    def on_modified(self, event):
        """Called when a directory of file is modified"""

        filehandle = os.path.abspath(event.src_path)
        if self.is_ignored_file(filehandle) or self.is_ignored_pattern(filehandle):
            if self.verbose:
                print("Skipping modified file: ", filehandle)
        else:
            if self.is_included_file(filehandle) or self.is_included_pattern(filehandle):
                if time.time() - self.time < 2:
                    pass
                else:
                    if self.verbose:
                        print("File: {} has been modified. scheduled {} callback starting soon".format(filehandle, self.callback))

                    self.time = time.time()
                    self.callback()

        super().on_modified(event)


class WatchDog:
    """A File system watchdog for file modifications.
    A wrapper around the watchdog.events.FileSystemEventHandler 
    and watchdog.observers.Observer that monitors for changes in file/dirs.
    Intended to simply server log reload

    @param: handler: An instance of wdog.EventHandler
    @param: folder_to_track: The absolute path of the base directory to track
    @param: recursive: Track files/folders in sub-folders if True
    @param: exclude_files: A list of files to ignore tracking.
    @param: include_patterns: A list of unix style file patterns to match files
    to track(Uses fnmatch.fnmatch(filename, pattern))
    Same applies to exclude patterns.
    """

    def __init__(self, callback,
                 handler=None,
                 folder_to_track=os.getcwd(),
                 recursive=False,
                 include_files=None,
                 exclude_files=None,
                 include_patterns=None,
                 exclude_patterns=None,
                 verbose=False):

        # If folder to track does not exist, raise error
        folder_to_track = os.path.expanduser(folder_to_track)
        if not os.path.exists(os.path.abspath(folder_to_track)):
            raise FileNotFoundError('No folder {}'.format(folder_to_track))

        # If no event handler, create one
        if handler is None:
            self.event_handler = EventHandler(callback, include_files, exclude_files,
                                              include_patterns, exclude_patterns)
        else:
            if isinstance(handler, EventHandler):
                self.event_handler = handler
            else:
                raise TypeError('Invalid EventHandler. Expected an instance of {}'.format(EventHandler.__class__))

        self.file_observer = Observer()
        self.file_observer.schedule(self.event_handler, folder_to_track, recursive)
        self.verbose = verbose

    def monitor_forever(self):
        """Monitor the file system in an infinite loop
        Press Ctrl-C to stop
        """

        if self.verbose:
            print('Starting watchdog...')

        self.file_observer.start()
        while True:
            try:
                time.sleep(1)
            except Exception:
                self.file_observer.stop()
                self.file_observer.join()
                raise
