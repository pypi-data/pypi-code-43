import platform

from django.utils.version import get_version as get_django_version
from packaging.version import Version

# TODO: Should I make this an optional import and fall back to pkg_resources?
#   "from pkg_resources import parse_version" is an alternative to requiring
#   the additional install of the packaging module.

DEFAULT_TABLE_ID = -1


# TODO: Should the flags live in a separate constants module?
# Get important version numbers for useful comparisons.
PYTHON_VERSION = Version(platform.python_version())
PYTHON_CONTEXT_VARIABLES_MINIMUM_VERSION = Version("3.7")
DJANGO_VERSION = Version(get_django_version())
DJANGO_SUBQUERY_EXPRESSION_MINIMUM_VERSION = Version("1.11")


# Version information based feature flags.
PYTHON_CONTEXT_VARIABLES_SUPPORT = (
    PYTHON_VERSION >= PYTHON_CONTEXT_VARIABLES_MINIMUM_VERSION
)
DJANGO_SUBQUERY_EXPRESSION_SUPPORT = (
    DJANGO_VERSION >= DJANGO_SUBQUERY_EXPRESSION_MINIMUM_VERSION
)


#


def compose_list(funcs):
    def inner(data, funcs=funcs):
        return inner(funcs[-1](data), funcs[:-1]) if funcs else data

    return inner


def import_from_string(class_path_str):
    last_dot_pos = class_path_str.rfind(".")
    class_name = class_path_str[last_dot_pos + 1 : len(class_path_str)]
    class_module = __import__(
        class_path_str[0:last_dot_pos], globals(), locals(), [class_name]
    )
    return getattr(class_module, class_name)


def is_url(context, value, original_value):
    from django.core.validators import URLValidator
    from django.core.exceptions import ValidationError
    from django.utils.translation import ugettext_lazy as _

    validate_url = URLValidator()
    try:
        validate_url(value)
    except ValidationError as e:
        raise ValidationError(_("This field must be a valid url"))
    return value
