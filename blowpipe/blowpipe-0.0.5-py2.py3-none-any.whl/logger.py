from datetime import datetime

TRACE = "TRACE"
DEBUG = "DEBUG"
INFO = "INFO"
WARN = "WARN"
ERROR = "ERROR"

TRACE_ENABLED = False
DEBUG_ENABLED = True
INFO_ENABLED = True
WARN_ENABLED = True
ERROR_ENABLED = True
CONSOLE_ENABLED = False

GLOBAL_OBSERVERS = []


class LogLine:
    """
    Entry representing a log line
    """
    # log_level: debug/info/warn
    # class: the calling python code/class or Console
    # indent_level: integer indicates how to structure
    # created: datetime of date created
    # message: str of log message
    # err if an exception raised
    # workflow_id if present the owning workflow
    # run_id if present the owning run_id

    def __init__(self, log_level, log_source, indent_level, created, message, workflow_id, run_id, username, err):
        self.log_level = log_level
        self.log_source = log_source
        self.indent_level = indent_level
        self.created = created
        self.message = message
        self.workflow_id = workflow_id
        self.run_id = run_id
        self.username = username
        self.err = err

    def to_string(self):
        DELIM = "|"
        msg = self.created.strftime("%Y-%m-%d %H:%M:%S") \
            + DELIM \
            + self.log_level \
            + DELIM \
            + self.log_source \
            + DELIM \
            + str(self.indent_level) \
            + DELIM \
            + self.username \
            + DELIM \
            + self.workflow_id \
            + DELIM \
            + self.run_id \
            + DELIM \
            + self.message
            # + DELIM \
            # + self.err
        return msg

    @staticmethod
    def from_string(source:str):
        DELIM = "|"
        splits = source.split(DELIM)
        created = datetime.strptime(splits[0], "%Y-%m-%d %H:%M:%S")
        log_level = splits[1]
        log_source = splits[2]
        indent_level = int(splits[3])
        username = splits[4]
        workflow_id = splits[5]
        run_id = splits[6]
        message = splits[7]
        return LogLine(log_level, log_source, indent_level, created, message, workflow_id, run_id, username, "")


class Logger:
    """
    own-rolled lightweight logger
    """

    def __init__(self, log_source:str):
        # the source of the logs (code/class/function)
        self.log_source = log_source
        # how many tabs to indent when rendering flat
        self.indent_level = 0
        # who was doing the thing
        self.username = ""
        # what was being operated on
        self.workflow_id = ""
        # which run was it
        self.run_id = ""
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        self.observers.remove(observer)

    def get_observers(self):
        return self.observers

    @staticmethod
    def add_global_observer(observer):
        GLOBAL_OBSERVERS.append(observer)

    @staticmethod
    def remove_global_observer(observer):
        GLOBAL_OBSERVERS.remove(observer)

    def get_global_observers(self):
        return GLOBAL_OBSERVERS

    @staticmethod
    def console(msg):
        # print("MSG=" + msg)
        entry = LogLine(log_level="DEBUG",
                        log_source="Console",
                        indent_level=0,
                        created=datetime.today(),
                        message=msg,
                        workflow_id="",
                        run_id= "",
                        username="",
                        err="")

        for observer in GLOBAL_OBSERVERS:
            observer.log(entry)

    def indent(self):
        self.indent_level += 1

    def unindent(self):
        self.indent_level -= 1

    def debug(self, msg):
        if DEBUG_ENABLED:
            self.log(DEBUG, datetime.today(), msg)

    def info(self, msg):
        if INFO_ENABLED:
            self.log(INFO, datetime.today(), msg)

    def warn(self, msg):
        if WARN_ENABLED:
            self.log(WARN, datetime.today(), msg)

    def trace(self, msg):
        if TRACE_ENABLED:
            self.log(TRACE, datetime.today(), msg)

    def error(self, msg, e):
        if ERROR_ENABLED:
            self.log(ERROR, datetime.today(), msg, e)

    def log(self, level, dt, msg, err=""):
        # entry = LogLine(level, self.log_source, self.indent_level, dt, str(msg), err)
        entry = LogLine(log_level=level,
                        log_source=self.log_source,
                        indent_level=self.indent_level,
                        created=dt,
                        message=msg,
                        workflow_id=self.workflow_id,
                        run_id=self.run_id,
                        username=self.username,
                        err=err)

        if CONSOLE_ENABLED:
            print("CONSOLE ENABLED: : " + str(entry))

        for observer in self.observers:
            observer.log(entry)

        for observer in GLOBAL_OBSERVERS:
            observer.log(entry)


class FileWriterObserver:
    def __init__(self, filename:str):
        self.filename = filename

    def log(self, entry:LogLine):
        f = open(self.filename, 'a')
        f.write(entry.to_string())
        f.write("\n")
        f.close()


