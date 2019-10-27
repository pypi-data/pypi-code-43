from django.conf import settings


def get_setting(name, default=None):
    name = 'HERALD_SLACK_%s' % name
    value = getattr(settings, name, default)
    return value


TOKEN = get_setting('TOKEN')
AS_USER = get_setting('AS_USER')
ICON_URL = get_setting('ICON_URRL')
USERNAME = get_setting('USERNAME')
