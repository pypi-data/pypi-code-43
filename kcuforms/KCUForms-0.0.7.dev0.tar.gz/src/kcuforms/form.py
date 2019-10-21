from flask_restful import reqparse

from kcuforms.errors import FieldError
from kcuforms.fields.core import BaseField, IntegerField, DictField

__all__ = ("WebForm", "SearchWebForm")


class BaseWebForm(object):
    """
    Base Form Class.  Provides core behaviour like field construction,
    validation, and data and error proxying.
    """
    pass


class WebFormMeta(type):
    """
    The metaclass for `Form` and any subclasses of `Form`.
    `FormMeta`'s responsibility is to create the `_unbound_fields` list, which
    is a list of `UnboundField` instances sorted by their order of
    instantiation.  The list is created at the first instantiation of the form.
    If any fields are added/removed from the form, the list is cleared to be
    re-generated on the next instantiation.
    Any properties which begin with an underscore or are not `UnboundField`
    instances are ignored by the metaclass.
    """

    def __new__(cls, name, bases, attrs):
        """
        Meta class of search form
        :param name: name of decorated class
        :param bases: base classes of decorated class
        :param attrs: attributes of decorated class
        :return: an instance of the type class
        """
        formfield = {}
        # define attributes from base classes
        for baseclazz in bases:
            if '__formfield__' in baseclazz.__dict__:
                formfield.update(baseclazz.__dict__['__formfield__'])
        # define attributes from current class
        for key, val in attrs.items():
            if isinstance(val, BaseField):
                val.name = key
                formfield[key] = val
        # del attribute key
        for key in formfield.keys():
            attrs.pop(key, None)

        attrs['__formfield__'] = formfield
        return super(WebFormMeta, cls).__new__(cls, name, bases, attrs)


class WebForm(BaseWebForm, metaclass=WebFormMeta):
    """
    Declarative Form base class. Extends BaseForm's core behaviour allowing
    fields to be defined on Form subclasses as class attributes.
    In addition, form and instance input data are taken at construction time
    and passed to `_validate_data()`.
    """
    __metaclass__ = WebFormMeta

    def __init__(self):

        self.parser = self._init_parser()

    def _init_parser(self):
        parser = reqparse.RequestParser()
        for field in self.__formfield__.values():
            kwargs = {}
            for attr in field.baseattrs:
                attr_val = getattr(field, attr)
                if attr_val is not None:
                    kwargs[attr] = attr_val
            parser.add_argument(**kwargs)
        return parser

    def get_form(self):
        try:
            args = self.parser.parse_args()
        except Exception as ex:
            raise FieldError(getattr(ex, 'data', ex))
        else:
            return self._validate_data(args)

    def _validate_data(self, args):
        for field in self.__formfield__.values():
            if field.name in args:
                val = args[field.name]
                args[field.name] = field.validate(val)
        return args


class SearchWebForm1(WebForm):
    page = IntegerField(default=0)
    size = IntegerField(default=10)


class SearchWebForm(WebForm):
    pagination = DictField(required=True, validators={
        'page': IntegerField(required=True, default=1),
        'size': IntegerField(required=True, default=10)
    })
