"""Distutil's setup.py"""


import os
import pathlib
import pipenv.project
import pipenv.utils
import setuptools as stt
import sphinx.setup_command
import subprocess  # nosec
import sys

_SETUP_DIR = pathlib.Path(sys.argv[0]).parent.resolve()
_VERSION = "0.2"  # sphinx: version and release; not used for wheels
_RELEASE = ".".join([_VERSION, "0"])  # used for wheel and sphinx
_NAME = "clalogger"
_GITHUB = 'https://github.com/mhooreman/clalogger'
_AUTHOR = 'Michaël Hooreman'
_COPYRIGHT = '2019, %s' % _AUTHOR
_LICENSE = 'MIT'


class _PipenvHelper:
    @property
    def project(self):
        """The pipenv project"""
        return pipenv.project.Project(_SETUP_DIR)

    @property
    def pipfile(self):
        """The pipenv's parsed pip file"""
        return self.project.parsed_pipfile

    @property
    def requirements(self):
        """The list of python requirements for production"""
        return pipenv.utils.convert_deps_to_pip(
            self.pipfile['packages'],
            r=False
        )

    @property
    def devRequirements(self):
        """The list of pyton requiremements for dev/test/build"""
        return pipenv.utils.convert_deps_to_pip(
            self.pipfile['dev-packages'],
            r=False
        )

    @property
    def pythonRequirements(self):
        """The required python version(s)"""
        return '>=%s' % self.pipfile['requires']['python_version']


def _getLongDescription():
    with open(_SETUP_DIR.joinpath('README.rst'), 'r') as fh:
        return fh.read()


def _updateApidocIfSphinx():
    if 'build_sphinx' not in sys.argv:
        return
    if any(['help' in x for x in sys.argv]):
        return
    subprocess.run(  # nosec
        ['/bin/bash', str(_SETUP_DIR.joinpath('doc', '_update-apidoc.sh'))],
        check=True
    )


def _setup(pipenvHelper):
    _updateApidocIfSphinx()
    stt.setup(
        name=_NAME,
        version=_RELEASE,
        description='Logging from class point of view, with easy config',
        long_description=_getLongDescription(),
        long_description_content_type='text/markdown',
        license=_LICENSE,
        url=_GITHUB,
        author=_AUTHOR,
        author_email='michael@hooreman.be',
        classifiers=[  # https://pypi.org/classifiers/
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Build Tools',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.7',
        ],
        keywords='logging stacktrace caller',
        package_dir={'': 'src'},
        packages=stt.find_packages(where='src'),
        include_package_data=True,
        install_requires=pipenvHelper.requirements,
        setup_requires=pipenvHelper.devRequirements,
        python_requires=pipenvHelper.pythonRequirements,
        extras_require={
            'dev': pipenvHelper.devRequirements,
        },
        project_urls={
            'Source': _GITHUB,
        },
        cmdclass={'build_sphinx': sphinx.setup_command.BuildDoc},
        command_options={
            'build_sphinx': {
                'project': ('setup.py', _NAME),
                'version': ('setup.py', _VERSION),
                'release': ('setup.py', _RELEASE),
                'source_dir': ('setup.py', 'doc'),
                'copyright': ('setup.py', _COPYRIGHT),
            }
        }
    )


def _main():
    _setup(_PipenvHelper())


if __name__ == "__main__":
    # chdir to the location of setup.py ...
    os.chdir(pathlib.Path(__file__).parent)
    # ... and run setup
    _main()
