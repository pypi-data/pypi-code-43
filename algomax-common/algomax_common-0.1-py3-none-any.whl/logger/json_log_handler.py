from logging import LogRecord, FileHandler

import os


class JSONLogHandler(FileHandler):
    """
    custom json log handler
    """

    def __init__(self, path):
        self.path = path
        self.terminator = ''
        FileHandler.__init__(self, path)

    def emit(self, record: LogRecord):
        """
        the base `emit` method has been overridden for format the `logfile` to JSON file format
        :param record: log record
        """
        if self.is_first_record():
            self.add_opening_bracket()
        else:
            self.remove_closing_bracket()
            self.add_comma()

        super().emit(record)

        self.add_closing_bracket()

    def is_first_record(self):
        """
        check if a log record is first log record or not
        :return: bool result: if a log record is first record return True else return False
        """
        with open(self.path, 'r') as log_handler:
            # get first line of logfile
            content = log_handler.readline()

        size_of_content = len(content)

        return size_of_content == 0

    def add_opening_bracket(self):
        """
        add opening bracket to the log file, formatting json log file
        """
        with open(self.path, 'w') as log_handler:
            log_handler.write('[\n')

    def add_comma(self):
        """
        add comma to (last - 1) log record, formatting json log file
        """
        with open(self.path, 'a') as log_handler:
            log_handler.write(',\n')

    def add_closing_bracket(self):
        """
        add closing bracket to end of logfile, formatting json log file
        """
        with open(self.path, 'a') as log_handler:
            log_handler.write('\n]\n')

    def remove_closing_bracket(self):
        """
        remove closing bracket for add new log record
        """
        with open(self.path, "r+", encoding="utf-8") as file:
            file.seek(0, os.SEEK_END)
            pos = file.tell() - 1

            while pos > 0 and file.read(1) != "\n":
                pos -= 1
                file.seek(pos, os.SEEK_SET)

            if pos > 0:
                file.seek(pos, os.SEEK_SET)
                file.truncate()
