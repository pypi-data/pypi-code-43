'''objectmapper exception classes'''
class ObjectMapperError(Exception):
    '''Parent exception class'''


class DuplicateMappingError(ObjectMapperError):
    '''Raised when a mapping between classes is redundantly defined without forcing an overwrite.'''
    def __init__(self, InputType, OutputType, mapping):
        super().__init__(f'Mapping already exists from {InputType} to {OutputType} -- {mapping}')


class MapTypeError(ObjectMapperError, TypeError):
    '''Raised when making a mapping between non-types, or map function is non-callable.'''


class MapInputKeyError(ObjectMapperError, KeyError):
    '''Raised when mapping an object of an unknown type.'''
    def __init__(self, InputType):
        super().__init__(f'No mappings found for instances of type {InputType}')


class MapOutputKeyError(ObjectMapperError, KeyError):
    '''Raised when mapping an object to an unknown type.'''
    def __init__(self, InputType, OutputType):
        super().__init__(f'No mappings found from instances of type {InputType} to type'
                         f' {OutputType}')
