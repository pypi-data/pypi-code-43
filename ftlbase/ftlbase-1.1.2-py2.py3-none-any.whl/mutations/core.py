from collections import namedtuple, defaultdict
import six

from . import fields
from . import error
from .util import wrap


Result = namedtuple('Result', ['success', 'return_value', 'errors'])
Result_Ok = Result(success=True, return_value=None, errors=error.ErrorDict())
ValidationResult = namedtuple('ValidationResult', ['is_valid', 'errors'])


class MutationBase(type):
    def __new__(mcs, name, bases, attrs):
        attrs.update({
            'fields': {},
            'validators': defaultdict(list),
            'extra_validators': defaultdict(list)
        })
        field_list, extra_validator_list = [], []

        for k, v in attrs.items():
            if isinstance(v, fields.FieldBase):
                field_list.append(k)
            elif isinstance(k, str) and k.startswith('validate_'):
                extra_validator_list.append(k)

        for f in field_list:
            field = attrs.pop(f)
            attrs['fields'][f] = field
            attrs['validators'][f].extend(wrap(field.validators))

        for v in extra_validator_list:
            validator = attrs.pop(v)
            attrs['extra_validators'][v].extend(wrap(validator))

        return super(MutationBase, mcs).__new__(mcs, name, bases, attrs)


@six.add_metaclass(MutationBase)
class Mutation(object):
    def __init__(self, name, inputs=None):
        self.name = inputs.pop('name',name)
        self.inputs = inputs or {}

    def __repr__(self):
        return '<Mutation {!r}>'.format(self.name)

    def __getattr__(self, name):
        if name in self.fields:
            return self._get_input(name)
        else:
            raise AttributeError

    def _validate(self):
        """Run all validations.

        We validate by doing the following:

        1. Validate base fields.
        2. Validate extra fields.

        If we encounter an error at any point along the way, mark that there has
        been at least one error. Then, try and continue validation, but if we
        run into another error (that is not a mutations error), terminate the
        validation process. This might be caused by whatever caused the initial
        validations.

        Returns a tuple: (was_successful, error_dict)
        """
        error_dict = error.ErrorDict()

        for field, validators in self.validators.items():
            value = self._get_input(field)
            for validator in validators:
                try:
                    valid = validator.validate(value)
                    if valid.has_error:
                        error_dict += valid
                except Exception as v:
                    err = "Mutation {} Exception {}".format(self.name, v)
                    error_dict[field].append(err)
                # if not success:
                #     error_dict[field].append(err)

        for validator_name, funcs in self.extra_validators.items():
            for func in funcs:
                try:
                    func(self)
                except error.ValidationError as err:
                    error_dict[validator_name].append(err.as_object())
                except Exception as exc:
                    error_dict[validator_name].append(exc)

        return error_dict

    def _get_input(self, field):
        if field in self.inputs:
            return self.inputs[field]
        elif self.fields[field].has_default:
            return self.fields[field].default
        return

    def execute(self):
        raise error.ExecuteNotImplementedError(
            "`execute` should be implemented by the subclass.")

    @classmethod
    def run(cls, raise_on_error=False, **kwargs):
        """Validate the inputs and then calls execute() to run the command. """
        instance = cls(cls.__name__, inputs = kwargs)
        error_dict = instance._validate()

        if error_dict.has_error:
            if raise_on_error:
                raise error.MutationFailedValidationError(error_dict)
            else:
                return Result(success=False, return_value=None, errors=error_dict)

        result = instance.execute()

        return Result(success=True, return_value=result, errors=error_dict)

    @classmethod
    def validate(cls, raise_on_error=False, **kwargs):
        instance = cls(cls.__name__, inputs = kwargs)
        error_dict = instance._validate()

        if error_dict.has_error:
            if raise_on_error:
                raise error.MutationFailedValidationError(error_dict)

        return error_dict
