from django.conf import settings


class LazySetting(object):
    def __init__(self, name, default=None):
        self.name = name
        self.default = default

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return getattr(obj._settings, self.name, self.default)


class LazySettings(object):
    def __init__(self, settings):
        self._settings = settings

    FIELD_BOOLEAN_ATTRS = LazySetting(
        name='FIELD_BOOLEAN_ATTRS',
        default=[
            'autofocus',
            'checked',
            'disabled',
            'formnovalidate',
            'multiple',
            'readonly',
            'required',
        ],
    )


settings = LazySettings(settings)
