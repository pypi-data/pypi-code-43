import datetime
import os
import sys
import argparse
import shutil
import subprocess
from pkg_resources import resource_string

from builtins import input
from jinja2 import Template

# String setuptools uses to specify None
UNKNOWN = "UNKNOWN"


PYTHON2_CONFIG = {
    'python_version': 'python',
    'python_package': 'python2.7-minimal',
    'python_bin': '/usr/bin/python2.7',
}

PYTHON3_CONFIG = {
    'python_version': 'python3',
    'python_package': 'python3.7-minimal',
    'python_bin': '/usr/bin/python3',
}


class DebianConfigurationException(Exception):
    pass


class DebianConfiguration(object):
    '''
    Given a root directory which contains a setup.py file,
    initializes debian configuration files in the debian directory
    '''

    DEBIAN_CONFIGURATION_TEMPLATES = [
        "resources/debian/changelog.j2",
        "resources/debian/compat.j2",
        "resources/debian/control.j2",
        "resources/debian/rules.j2",
    ]

    DEFAULT_CONTEXT = {
        "compat": 9,
    }

    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.context = self.DEFAULT_CONTEXT.copy()
        self.context.update({"date": datetime.datetime.now()})
        self.context.update(self._context_from_setuppy())
        if self.not_in_context('changelog'):
            self.context.update(self._context_from_git())
        self.context.update(self._context_from_cmdline_args())
        self.context.update(self._context_from_context())

    def not_in_context(self, key):
        return (key not in self.context or
                self.context[key] == UNKNOWN)

    def _context_from_context(self):
        update = {}
        # Move author in maintainer if not defined
        if self.not_in_context('maintainer') and 'author' in self.context:
            update.update({'maintainer': self.context['author']})
        if (self.not_in_context('maintainer_email')
                and 'author_email' in self.context):
            update.update(
                {'maintainer_email': self.context['author_email']})
        return update

    def _context_from_git(self):
        try:
            stdout = subprocess.Popen(
                ["git", "log", "-1", "--oneline"],
                cwd=self.rootdir,
                stdout=subprocess.PIPE).communicate()
            return {"changelog": '  * ' + stdout[0].decode()}
        except OSError:
            raise DebianConfigurationException("Please install git")
        except Exception as e:
            raise DebianConfigurationException(
                "Unknown error occurred when invoking git: %s" % e)

    def _context_from_setuppy(self):
        setuppy_path = os.path.join(self.rootdir, "setup.py")
        if not os.path.exists(setuppy_path):
            raise DebianConfigurationException("Failed to find setup.py")
        stdout = subprocess.Popen(
            ["python", os.path.join(self.rootdir, "setup.py"),
             "--name", "--version", "--maintainer", "--maintainer-email",
             "--author", "--author-email",
             "--description"], stdout=subprocess.PIPE).communicate()

        long_description_stdout = subprocess.Popen(
            ["python", os.path.join(self.rootdir, "setup.py"),
             "--long-description"], stdout=subprocess.PIPE).communicate()

        setup_values = stdout[0].decode('utf-8').split('\n')[:-1]
        setup_values.append(long_description_stdout[0].decode('utf-8')[:-1])
        setup_names = ["name", "version", "maintainer", "maintainer_email",
                       "author", "author_email", "description", "changelog"]

        context = {}
        for name, value in zip(setup_names, setup_values):
            if value or value != UNKNOWN:
                context[name] = value
        return context

    def _context_from_cmdline_args(self):
        ctx = {}
        parser = argparse.ArgumentParser(description='')
        parser.add_argument('--python2', action='store_true',
                            help='Generate python2 venv (default python3)')
        parser.add_argument('--install-dir', type=str, default='/opt/venvs/',
                            help='Where to install the venv '
                                 'when installing package')
        parser.add_argument('--shlibdeps', type=str,
                            default='-X/x86/ -X/psycopg2/.libs',
                            help='Where to search for lib dependencies')
        args = parser.parse_args()
        python_conf = PYTHON3_CONFIG
        if args.python2:
            python_conf = PYTHON2_CONFIG
        ctx.update(python_conf)
        ctx.update({'shlibdeps': args.shlibdeps,
                    'dh_virtualenv_install_root': args.install_dir})
        return ctx

    def render(self):
        output_dir = os.path.join(self.rootdir, "debian")

        if os.path.exists(output_dir):
            print('Removing existing debian directory')
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)

        for template in self.DEBIAN_CONFIGURATION_TEMPLATES:
            filename = os.path.basename(template).replace(".j2", "")
            content = Template(
                resource_string("python_make_deb", template).decode('utf-8')
            ).render(self.context)

            with open(os.path.join(output_dir, filename), "w") as f:
                f.write(content)

        # Need to to trigger separately because filename must change
        trigger_content = Template(
            resource_string("python_make_deb",
                            "resources/debian/triggers.j2").
            decode('utf-8')
        ).render(self.context)

        trigger_filename = "%s.triggers" % self.context['name']
        with open(os.path.join(output_dir, trigger_filename), "w") as f:
            f.write(trigger_content+"\n")


def main():
    try:
        debconf = DebianConfiguration(os.getcwd())
        debconf.render()
    except DebianConfigurationException as e:
        print(e)
        return 1

    print("'debian' directory successfully placed at the "
          "root of the repository")
    return 0


if __name__ == "__main__":
    sys.exit(main())
