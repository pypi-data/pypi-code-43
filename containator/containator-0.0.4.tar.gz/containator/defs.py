__version__ = '0.0.4'
app_name = 'Containator'
app_description = 'Runs docker containers with pre-defined parameters'
app_version = '{} {}'.format(app_name, __version__)
app_name_desc = '{} - {}'.format(app_name, app_description)

CONFIG_FILES = ['/etc/containator.conf', '~/.config/containator.conf', '~/.containator.conf']
