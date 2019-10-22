from collections import namedtuple


class ErrorSource(Exception):

    def __init__(self, *args, source=None, **kwargs):
        self.source = source or ''
        super().__init__(*args, **kwargs)

    def __str__(self):
        output = super().__str__()
        output = f'{output}: {self.source}'
        return output


class ExceptionList(Exception):

    def __init__(self, exceptions):
        self.exceptions = exceptions
        suffix = 's' if len(exceptions) > 1 else ''
        super().__init__(f'{len(self.exceptions)} error{suffix} occured:')

    def __str__(self):
        output = super().__str__()
        for exception in map(str, self.exceptions):
            output += f'\n  {exception}'
        return output


class LazyErrors:

    def __init__(self):
        self.errors = []

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.errors != []:
            raise ExceptionList(self.errors)
        return None

    def error(self, exception):
        self.errors.append(exception)
        return None
