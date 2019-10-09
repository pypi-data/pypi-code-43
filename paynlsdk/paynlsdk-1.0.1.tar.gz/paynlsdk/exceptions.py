
class ErrorException(Exception):
    def __init__(self, error):
        self.error = error
        message = error.message
        super(ErrorException, self).__init__(message)


class SchemaException(Exception):
    def __init__(self, error_dict):
        self.errors = error_dict
        message = self._convert_errors(error_dict)
        super(SchemaException, self).__init__(message)

    @classmethod
    def _key(self, k: str, prefix: str=''):
        """
        Format a prefix/key combination
        :param k: current key
        :type k: str
        :param prefix: current prefix
        :type prefix: str
        :return: formatted key/prefix combination for use with message output
        :rtype: str
        """
        if prefix == '':
            return k
        else:
            return prefix + '.' + k

    @classmethod
    def _convert_errors(self, errors, depth: int = 0, prefix: str = ''):
        """
        Convert an error object into a readable format.

        Readable format means we transform any recursion depth to a dot separated key
        Errors then get the following format: obj.subobj.field: errornessage

        :param errors: variable error
        :type errors: object
        :param depth: current formatting depth
        :type depth: int
        :param prefix: current prefix
        :type prefix: str
        :return: formatted errors
        :rtype: str
        """
        if isinstance(errors, dict):
            return '\n'.join(['{}'.format(self._convert_errors(v, depth+1, self._key(k, prefix)))
                              for k, v in errors.items()])
        elif isinstance(errors, list):
            if prefix == '':
                return ', '.join(errors)
            else:
                return prefix + ': ' + ', '.join(errors)
        else:
            if prefix == '':
                return str(errors)
            else:
                return prefix + ': ' + str(errors)


class TransactionNotAuthorizedException(Exception):
    def __init__(self, message):
        super(TransactionNotAuthorizedException, self).__init__(message)


class TransactionStatusException(Exception):
    def __init__(self, message):
        super(TransactionStatusException, self).__init__(message)

