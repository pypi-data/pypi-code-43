from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

SETTINGS_NAMESPACE = "ACTIONABLE_MESSAGES"
DEFAULTS = {
    "JSON_ENCODER": None
}


def import_from_string(value, name):
    try:
        return import_string(value)
    except ImportError:
        raise ImportError("Could not import '{}' setting".format(name))


def import_setting(value, name):
    if value is None:
        return None
    elif isinstance(value, str):
        return import_from_string(value, name)
    return value


class CardSettings:
    def __getattr__(self, attr):
        if attr not in DEFAULTS:
            raise AttributeError("Invalid setting: '{}'".format(attr))
        try:
            value = self.user_settings[attr]
        except KeyError:
            value = DEFAULTS[attr]
        return import_setting(value, attr)

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, SETTINGS_NAMESPACE, {})
        return self._user_settings

    def reload_user_settings(self):
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


card_settings = CardSettings()


def reload_settings(*args, **kwargs):
    setting = kwargs["setting"]
    if setting == SETTINGS_NAMESPACE:
        card_settings.reload_user_settings()


setting_changed.connect(reload_settings)
