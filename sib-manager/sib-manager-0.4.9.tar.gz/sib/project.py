import subprocess
import sys
import logging
import yaml
import os
from importlib import import_module
from pkg_resources import resource_filename


logger = logging.getLogger(__name__)


class Project(object):

    """
    This class initialize a new SIB project by installing the required components and configuring the project
    """

    def __init__(self, name, folder):

        """
        Initialization
        """

        # set project params
        self.name = name
        self.folder = folder
        self.deps_file = os.path.join(folder, 'packages.yml')

    def get_template(self, production):

        """Return the path of django project template from package resouces"""

        if production:
            return resource_filename(__name__, 'templates/production')

        return resource_filename(__name__, 'templates/development')

    def get_dists(self):

        """Return the list of distribution configured"""

        try:
            with open(self.deps_file, 'r') as f:
                packages = yaml.safe_load(f).get('ldppackages')

            dists = list(packages.values())
            logger.debug('configured packages {}'.format(dists))
            return dists

        except AttributeError:
            logger.info('No LDP packages found')
            return []

    def get_config(self):

        """Return the configuration as dictionary"""

        try:
            with open(self.deps_file, 'r') as f:
                return yaml.safe_load(f).get('server')

        except AttributeError:
            logger.error('No configuration found')
            return {}

    def is_venv(self):

        """
        Tells if the program runs in a virtualenv

        This is a helper function as the python programer should know to use
        a virtualenv (and incompatibility with --user install)
        """

        if (hasattr(sys, 'real_prefix') or
            (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)):
            logger.info('virtualenv detected')
            return True
        return False

    def create(self, production):

        """Create the SIB project"""

        try:
            try:
                import django
                import djangoldp
            except ModuleNotFoundError:
                # install djangoldp (and gets the right version of django as dependency)
                cmd = ['pip', 'install', 'djangoldp']
                if not self.is_venv():
                    cmd.append('--user')
                subprocess.run(cmd).check_returncode()

            # force installation of psycopg for prd
            if production:
                try:
                    import psycopg2
                except ModuleNotFoundError:
                    cmd = ['pip', 'install', 'psycopg2']
                    if not self.is_venv():
                        cmd.append('--user')
                    subprocess.run(cmd).check_returncode()

            try:
                os.mkdir(self.folder)
            except FileExistsError:
                logger.error(f'Directory {self.folder} already exists')
                raise

            # init django project
            # call subprocess to avoid django settings initialization in main thread
            cmd = ['django-admin',
                'startproject',
                '--template', self.get_template(production),
                self.name,
                self.folder
            ]

            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True).check_returncode()

        except subprocess.CalledProcessError as e:
            logger.error(e.stderr)
            raise

    def install(self):

        """Install distributions"""

        try:
            if self.get_dists():

                cmd = ['pip', 'install', '--upgrade']
                if not self.is_venv():
                    cmd.append('--user')
                cmd.extend(self.get_dists())

                subprocess.run(cmd).check_returncode()

        except subprocess.CalledProcessError as e:
            logger.error('Installation failed: {}'.format(e))
            raise

    def load(self):

        """
        Load the project
        Warning: this step initialize django.setup() which can't be unloaded
        so this function can only be executed once per python instance
        """

        try:
            # django imports
            import django
            from django.conf import settings
            from django.core import management
            from django.core.exceptions import ImproperlyConfigured
            from django.core.management.base import CommandError

            # load sib project settings
            if settings.configured:
                raise RuntimeError('Can\'t override django settings')

            sys.path.append(self.folder)
            sib_settings = import_module(self.name + '.settings')
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', sib_settings.__name__)

            # setup the django sib project
            django.setup()

        except ModuleNotFoundError as e:
            logger.error(e)
            raise

        except ImportError as e:
            logger.error('Project not initialized: {}'.format(e))
            raise

        try:
            # migrate data
            management.call_command('migrate', interactive=False)

        except ImproperlyConfigured as e:
            logger.error('Django configuration failed: {}'.format(e))
            raise

        except CommandError as e:
            logger.error('Django migration failed: {}'.format(e))
            raise

        try:
            logger.debug('Admin name: {}'.format(self.get_config()['admin_name']))
            # create superuser
            from django.contrib.auth import get_user_model
            User = get_user_model()
            User.objects.create_superuser(
                self.get_config().get('admin_name'),
                self.get_config().get('admin_email'),
                self.get_config().get('admin_pass')
            )

        except django.db.utils.IntegrityError:
            logger.info('Admin {} already exists'.format(self.get_config().get('admin_name')))
            pass

        except (TypeError, ValueError) as e:
            logger.error('Super user creation failed: configuration parameters missing')
            logger.debug('Super user creation failed: {}'.format(e))
            raise

        try:
            # creatersakey
            management.call_command('creatersakey', interactive=False)

        except CommandError:
            logger.info('Create RSA key failed')
            pass
