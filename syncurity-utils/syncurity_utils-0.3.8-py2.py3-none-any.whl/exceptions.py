""" syncurity_utils.exceptions

This module contains exceptions that are common to the syncurity-utils package

:copyright: (c) 2019 Syncurity
:license: Apache 2.0, see LICENSE.txt for more details
"""

__all__ = ['SyncurityException', 'TypecheckError', 'SubmissionError']


class SyncurityException(Exception):
    """ Generic exception that may have occurred during a function call from this package """
    def __init__(self, message, errors=None):
        super(SyncurityException, self).__init__(message)

        self.errors = errors


class TypecheckError(SyncurityException):
    """ Exception raised when typechecking from the typecheck module fails """
    def __init__(self, message, errors=None):
        super(TypecheckError, self).__init__(message)

        self.errors = errors


class SubmissionError(SyncurityException):
    """ Exception raised when a fact group or other object couldn't be sent to IR-Flow """
    def __init__(self, message, errors=None):
        super(SubmissionError, self).__init__(message)

        self.errors = errors
