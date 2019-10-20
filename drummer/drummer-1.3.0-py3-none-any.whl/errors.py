# -*- coding: utf-8 -*-

"""This modules provides the error messages used by drummer components."""

class Errors:
    """Class for error messages."""

    E0000 = 'Configuration file not found'
    E0001 = 'Task file not found'
    E0002 = 'Verbosity level must be between 0 and 3.'

    E0100 = 'Data must be a serializable <dict>'
    E0101 = 'Message cannot be decoded'
    E0102 = 'Classname must be a string'
    E0103 = 'Classpath must be a string'
    E0104 = 'Status code not supported'

    E0200 = 'Socket has refused connection'
    E0201 = 'Generic connection error'
    E0202 = 'Impossible to send the request to server'
    E0203 = 'Socket breakdown'
    E0204 = 'Error in server socket'
