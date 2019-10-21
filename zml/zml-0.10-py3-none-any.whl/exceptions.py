class DocumentNotDefinedException(Exception):
    message = 'Call to get_absolute_path without document parameter and no document set'


class FileNotLoadedException(Exception):
    message = 'Could not load file'


class IndentationException(Exception):
    message = 'Indentation not a multiple of two'


class VariableNotDefinedException(Exception):
    message = 'Variable not defined'


class TranslationNotDefinedException(Exception):
    message = 'Translation not defined'


class NotFoundException(Exception):
    message = 'Route can not be resolved'
