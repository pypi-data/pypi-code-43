from ingaia.commons.exceptions import GenericException


class NoOpenAPIFileConfiguredException(GenericException):
    message = 'You must inform an openapi configuration file'
