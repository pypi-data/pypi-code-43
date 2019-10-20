from collections import namedtuple

from six.moves import UserDict

from copy import deepcopy


class MutationError(Exception):
    pass


class ErrorDict(UserDict):
    def __init__(self, *args, **kwargs):
        self.default_factory = kwargs.pop('default_factory', list)
        err = kwargs.pop('err', None)
        msg = kwargs.pop('msg', None)
        super().__init__(self, *args, **kwargs)
        if err and msg:
            self[err].append(msg)

    def __getitem__(self, k):
        if not k in self.data:
            self.data[k] = self.default_factory()
        return self.data[k]

    def __add__(self, other):
        if self.default_factory != other.default_factory:
            raise MutationError("Cannot add two ErrorDicts with different default_factories.")
        result = self.copy()
        if result.keys() & other.keys():
            for key, val in other.items():
                if key in result.data:
                    result[key] += val
                else:
                    result[key] = val
        else:
            result.update(other)
        # context = {}
        # context.update(self)
        # if context.keys() & other.keys():
        #     for key, val in other.items():
        #         if key in context:
        #             context[key] += val
        #         else:
        #             context[key] = val
        # else:
        #     context.update(other)
        # return ErrorDict(context, default_factory=self.default_factory)
        return result

    @property
    def has_error(self):
        return bool(self.data)

    @property
    def is_empty(self):
        return not self.has_error

    def __str__(self):
        msg = ''
        for i in self.data:
            for j in self.data[i]:
                msg += '{} - {}\n'.format(i, str(j))
        return msg


ErrorBody = namedtuple('ErrorBody', ['err', 'msg'])


class ValidationError(MutationError):
    def __init__(self, err=None, msg=None, *args, **kwargs):
        self.err = err
        self.msg = msg
        super().__init__(self, *args, **kwargs)

    def __str__(self):
        msg = ''
        if hasattr(self, 'msg'):
            msg = str(self.msg)
        if hasattr(self, 'error_dict'):
            for i in self.error_dict:
                for j in self.error_dict[i]:
                    if isinstance(j, ErrorBody):
                        msg += 'validator {}: {}\n'.format(i, j.msg)
                    else:
                        msg += '{} - {}\n'.format(i, str(j))
        return msg

    def as_object(self):
        # return ErrorBody(err=self.err, msg=self.msg)
        return ErrorDict(err=self.err, msg=self.msg)


class MutationFailedValidationError(ValidationError):
    def __init__(self, error_dict={}):
        self.error_dict = error_dict


class ExecuteNotImplementedError(NotImplementedError, MutationError):
    pass

# class ValidationResult(object):
#     """ Resultado da validação é um list de campo e descrição de erros e
#         um list de erros globais, não diretamente ligados a campo, mas ao objeto em si """
#     def __init__(self, *args, **kwargs):
#         self.global_errors = []  # list de mensagens
#         self.field_errors = []  # list de { field: errors[] }
#         super().__init__(self, *args, **kwargs)
#
#     @property
#     def has_error(self):
#         return bool(self.global_errors) or bool(self.field_errors.count())
#
#     def add_global_errors(self, validator, errors):
#         if not isinstance(validator, str):
#             raise MutationError("ValidationResult: add_global_errors: Invalid type {} for validator.".format(type(field)))
#         if not isinstance(errors, list):
#             raise MutationError("ValidationResult: add_global_errors: Invalid type {} for errors.".format(type(errors)))
#
#         self.global_errors.append({field: errors})
#
#     def add_field_errors(self, field, errors):
#         if not isinstance(field, str):
#             raise MutationError("ValidationResult: add_field_errors: Invalid type {} for field.".format(type(field)))
#         if not isinstance(errors, list):
#             raise MutationError("ValidationResult: add_field_errors: Invalid type {} for errors.".format(type(errors)))
#
#         self.field_errors.append({field: errors})
#
#     def __str__(self):
#         msg = ''
#         for i in self.global_errors:
#             for j in self.global_errors[i]:
#                 msg += '{} - {}\n'.format(i, str(j))
#         for i in self.field_errors:
#             for j in self.field_errors[i]:
#                 msg += '{} - {}\n'.format(i, str(j))
#         return msg
