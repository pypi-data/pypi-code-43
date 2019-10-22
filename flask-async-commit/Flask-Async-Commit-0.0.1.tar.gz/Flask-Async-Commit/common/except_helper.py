# coding: utf-8


class TableNotFound(Exception):
    def __init__(self, *args):
        super(TableNotFound, self).__init__(*args)


class DataBaseCommitError(Exception):
    def __init__(self, *args):
        super(DataBaseCommitError, self).__init__(*args)


class ComputeException(Exception):
    def __init__(self, *args):
        super(ComputeException, self).__init__(*args)


class MacFormatError(Exception):
    def __init__(self, *args):
        super(MacFormatError, self).__init__(*args)