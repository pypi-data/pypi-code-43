from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry
from dynamic_preferences.types import StringPreference


robot = Section('robot')


@global_preferences_registry.register
class LinkTemplate(StringPreference):
    section = robot
    name = 'link_template'
    default = 'http://example.com/{}'


@global_preferences_registry.register
class UploadDirectory(StringPreference):
    section = robot
    name = 'upload_directory'
    default = '/tmp'


@global_preferences_registry.register
class TwitterAPIToken(StringPreference):
    section = robot
    name = 'twitter_api_token'
    default = ''
