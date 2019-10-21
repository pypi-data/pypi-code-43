from functools import wraps

from kcuforms.errors import FieldError


def field_exception(func):
    """
    Add field information to the exception
    :return:
    """

    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except FieldError as ex:
            ex.STATUS = 'FIELD NAME: {}, INFO: '.format(self.name) + ex.STATUS
            raise ex

    return wrapped_func
