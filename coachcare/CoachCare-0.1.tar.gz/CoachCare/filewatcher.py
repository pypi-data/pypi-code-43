import os, time
from threading import Thread
from CoachCare.constants import FILE_WATCHER_DIR
from CoachCare.constants import logging
from CoachCare.templateEngine.utils.pubsub import Publisher

logging = logging.getLogger(__name__)
class FileWatcher(Publisher):
    def __init__(self, path=None, file_type=None, group=None, validator=None, target=None,
                 name=None, args=(), kwargs={}, Verbose=None):
        #validators must return True or False
        Publisher.__init__(self)
        self._return =None

        if path == None:
            self.dir = FILE_WATCHER_DIR 
        else:
            self.dir = path
        if file_type == None:
            self.file_type = "hl7"
        else:
            self.file_type = file_type
        self.file_type = "." + self.file_type
        self.added = None
        self.pool_interval = 0
        self.validator = validator

    def _get_files_in_dir(self):
        return [(file, None) for file in os.listdir(self.dir) if file.lower().endswith(self.file_type) ]

    def _is_file_written(self):
        assert type(self.pool_interval) is int
        state_before = dict(self._get_files_in_dir())
        while True:
            state_after = dict(self._get_files_in_dir())
            added = [file for file in state_after if file not in state_before]
            state_before = state_after
            if added:
                # if validator function is required wait till it turn true to
                # exit loop
                if self.validator:
                    valid = self.validator(self.dir + added[0])
                    if valid:
                        self.added = added[0]
                        break
                else:
                    self.added = added[0]
                    break
            time.sleep(self.pool_interval)

    def check_for_ack(self, file_added):
        pass     

    def watch(self, *args, handler=None, validator=None, **kwargs):
        logging.debug("[FileWatcher] watching: " + self.dir)
        self._is_file_written()
        if handler:
            logging.debug("[FileWatcher] calling handler function named: " + handler.__name__)
            if "file_added" in handler.__code__.co_varnames:
                return handler(file_added=self.added, *args, **kwargs)
            return handler(*args, **kwargs)
        return {"file_added": self.added}
            
