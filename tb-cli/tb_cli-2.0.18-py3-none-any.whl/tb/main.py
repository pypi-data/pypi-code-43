import glob
import os

from cement import init_defaults, App
from cement.core.exc import CaughtSignal

from tb.config import configured_org_repo_dir
from tb.config import get_bundle_dir, get_default_config_dir
from tb.first_time import read_user_config
from tb.tb import Tb, set_default_env
from .controllers.base import Base
from .core.exc import TbError

# configuration defaults
CONFIG = init_defaults('tb')


bundle_dir = get_bundle_dir()
default_config_dir = get_default_config_dir()

default_config_files = [os.path.join(default_config_dir, f) for f in glob.glob1(default_config_dir, "*.yml")]

plugin_dirs = [os.path.join(bundle_dir, 'plugins'), os.path.join(".tb", "plugins")]
plugin_config_dirs = [os.path.join(bundle_dir, 'plugins.d'), os.path.join(".tb", "plugins.d")]
env_config_files = []
team_config_files = []

config = read_user_config()
if config['tb']:
    org_repo_dir = configured_org_repo_dir(config)
    if os.path.isdir(org_repo_dir):
        team_config_files = [os.path.join(org_repo_dir, f) for f in glob.glob1(org_repo_dir, "*.yml")]
        plugin_dirs.append(os.path.join(org_repo_dir, 'plugins'))
        plugin_config_dirs.append(os.path.join(org_repo_dir, 'plugins.d'))
    else:
        team_config_files = []
        # print("No configuration found")
        # sys.exit(1)

    env_config_files = [d for d in (os.environ.get("TB_CONFIG").split(",")
                                    if os.environ.get("TB_CONFIG") is not None else [])]

    # read plugins out of a local tb checkout, if available
    local_tb_src_dir = os.path.join(config['tb']['src_dir'], 'tb')
    if os.path.isdir(local_tb_src_dir):
        plugin_dirs.append(os.path.join(local_tb_src_dir, 'plugins'))
        plugin_config_dirs.append(os.path.join(local_tb_src_dir, 'plugins.d'))


class TbConfigured(Tb):
    """Team B CLI primary application."""

    class Meta:
        label = 'tb'

        # configuration defaults
        config_defaults = CONFIG

        config_files = \
            default_config_files + \
            team_config_files + \
            ['~/.tb/tb.yml', 'tb.yml'] + \
            env_config_files

        config_dirs = plugin_config_dirs

        # call sys.exit() on close
        close_on_exit = True

        # load additional framework extensions
        extensions = [
            'yaml',
            'colorlog',
            'jinja2'
        ]

        core_extensions = [x for x in App.Meta.core_extensions if x != 'cement.ext.ext_plugin'] + \
                          ['tb.ext.ext_versionedplugins']

        plugin_dirs = plugin_dirs

        # configuration handler
        config_handler = 'yaml'

        # configuration file suffix
        config_file_suffix = '.yml'

        # set the log handler
        log_handler = 'colorlog'

        plugin_handler = 'versionedplugins'

        # set the output handler
        output_handler = 'jinja2'

        hooks = [
            ('post_argument_parsing', set_default_env),
        ]

        # register handlers
        handlers = [
            Base
        ]


def main():
    with TbConfigured() as app:
        try:
            app.run()

        except KeyboardInterrupt:
            app.exit_code = 1

        except AssertionError as e:
            if e.args:
                print('AssertionError > %s' % e.args[0])
            app.exit_code = 1

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except TbError as e:
            app.term.error('Error: %s' % e.args[0])
            app.exit_code = e.exit_code

            if app.debug is True:
                import traceback
                traceback.print_exc()

        except CaughtSignal as e:
            # Default Cement signals are SIGINT and SIGTERM, exit 0 (non-error)
            print('\n%s' % e)
            app.exit_code = 0


if __name__ == '__main__':
    main()
