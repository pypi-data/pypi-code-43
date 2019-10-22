class ExceptionDesc:

    message = ""
    cause = ""
    assertionError = False
    stackTrace = []
    additionalInfo = ""

    def __init__(self, exception):
        message = ''
        if getattr(exception, 'message', None) is not None:
            message = exception.message
        if getattr(exception, 'msg', None) is not None:
            message = exception.msg
        self.message = message
        #self.cause = exception.cause
        #self.assertionError = exception.assertionError
        #self.stackTrace = exception.stackTrace
        #self.additionalInfo = exception.additionalInfo

    def gen_row_value(self, lst=['message', 'cause', 'assertionError', 'stackTrace', 'additionalInfo']):
        row_value = {}

        for a in lst:
            row_value[a] = getattr(self, a)
        return row_value
