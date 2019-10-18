from .error import ErrorBody, ErrorDict


class ValidatorBase(object):
    def validate(self, *args, **kwargs):
        valid = self.is_valid(*args, **kwargs)
        if not valid:
            return self.get_error(*args, **kwargs)
        else:
            return ErrorDict()

    def is_valid(self, val):
        raise NotImplementedError()

    def get_error(self, val):
        err = self.__class__.__name__
        msg = "%s failed with input %r." % (self.__class__.__name__, val)
        return ErrorDict(err=err, msg=msg)


class RequiredValidator(ValidatorBase):
    def is_valid(self, val):
        return val is not None


class NotBlankValidator(ValidatorBase):
    def is_valid(self, val, strip=False):
        if strip:
            return val.strip() != ''
        else:
            return val != ''


class InstanceValidator(ValidatorBase):
    def __init__(self, instance_of, required = False, *args, **kwargs):
        if not isinstance(instance_of, (list, tuple)):
            instance_of = (instance_of,)
        self.instance_of = instance_of
        self.required = required
        super().__init__(*args, **kwargs)

    def is_valid(self, val):
        return isinstance(val, self.instance_of) or (val is None and not self.required)


class CustomValidator(ValidatorBase):
    def __init__(self, func, *args, **kwargs):
        self.func = func
        super().__init__(*args, **kwargs)

    def is_valid(self, *args, **kwargs):
        return self.func(*args, **kwargs)


class YesValidator(ValidatorBase):
    """ Always True """
    def is_valid(self, *args, **kwargs):
        return True


class SavedObjectValidator(ValidatorBase):
    """ If objects has already been saved """
    def is_valid(self, obj):
        return obj._state.adding
        # ==> Não é garantia, por exemplo em Estado não funciona, pois a pk é informada (sigla)
        # return obj.pk is not None and obj.pk != ''


class StatusValidator(ValidatorBase):
    """ Validate a informed status if is valid according valid_statues """
    def __init__(self, valid_statuses, required=False, *args, **kwargs):
        if not isinstance(valid_statuses, (list, tuple)):
            valid_statuses = (valid_statuses,)
        self.valid_statuses = valid_statuses
        self.required = required
        super().__init__(*args, **kwargs)

    def is_valid(self, val):
        return val in self.valid_statuses or (not self.required and val is None)
