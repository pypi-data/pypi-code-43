#######################
## Public exceptions
#######################
class NonStreamException(Exception):
    """The stream is expected to be a file-type object"""
    pass

class StreamUnexpectedlyClosed(Exception):
    """The stream got closed while we were reading it"""
    pass

class rePatternError(Exception):
    """The pattern received cannot be compiled"""
    pass


#######################
## Private exceptions
#######################
class _TimeOutOccured(Exception):
    """No (enough) data could be read from the stream"""
    pass
