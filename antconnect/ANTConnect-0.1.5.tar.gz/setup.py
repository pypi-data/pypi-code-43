import io
import os
import pip
import re
import sys

try: # for pip >= 10
    from pip._internal.req import parse_requirements
    from pip._internal import download
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

from distutils.sysconfig import get_python_lib
from setuptools import find_packages
from setuptools import setup

CURRENT_PYTHON = list(sys.version_info[:2])
REQUIRED_PYTHON = list(map(int, "3.5".split(".")))

# This check and everything above must remain compatible with Python 2.7.
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version
==========================
This version of antconnect requires Python {}.{}, but you're trying to install it on Python {}.{}.
This may be because you are using a version of pip that doesn't understand the python_requires classifier. Make sure you have pip >= 9.0 and setuptools >= 24.2, then try again:
    $ python -m pip install --upgrade pip setuptools
    $ python -m pip install antconnect
""".format(*(REQUIRED_PYTHON + CURRENT_PYTHON)))
    sys.exit(1)

# Warn if we are installing over top of an existing installation. This can
# cause issues where files that were deleted from a more recent version are
# still present in site-packages.
overlay_warning = False
if "install" in sys.argv:
    lib_paths = [get_python_lib()]
    if lib_paths[0].startswith("/usr/lib/"):
        # We have to try also with an explicit prefix of /usr/local in order to
        # catch Debian's custom user site-packages directory.
        lib_paths.append(get_python_lib(prefix="/usr/local"))
    for lib_path in lib_paths:
        existing_path = os.path.abspath(os.path.join(lib_path, "antconnect"))
        if os.path.exists(existing_path):
            # We note the need for the warning here, but present it after the
            # command is run, so it's more likely to be seen.
            overlay_warning = True
            break



#-----#
# The section below parses the requirements file and converst it to a list of 
# requirements to be used within the setup.
#-----#
links = []  # for repo urls (dependency_links)
requires = []  # for package names
try:
    # new versions of pip requires a session
    requirements = parse_requirements(
        'requirements.txt', session=download.PipSession()
    )
except:
    requirements = parse_requirements('requirements.txt')

for item in requirements:
    if getattr(item, 'url', None):  # older pip has url
        links.append(str(item.url))
    if getattr(item, 'link', None):  # newer pip has link
        links.append(str(item.link))
    if item.req:
        requires.append(str(item.req))  # always the package name 
#-----#       


def read(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    text_type = type(u"")
    with io.open(filename, mode="r", encoding='utf-8') as fd:
        return re.sub(text_type(r':[a-z]+:`~?(.*?)`'), text_type(r'``\1``'), fd.read())



setup_requirements = ['pytest-runner',]
test_requirements = ['pytest', ]

# Add readme to the file
with open('README.rst') as readme_file:
    readme = readme_file.read()

# Add changelog to the file
with open('CHANGELOG.rst') as history_file:
    history = history_file.read()

setup(
    name="ANTConnect",
    version="0.1.5",
    url="",
    license='Proprietary',

    author="ANTCDE",
    author_email="info@antcde.io",
    description="Provides access to an ant CDE",
    long_description=readme + '\n\n' + history,
    
    packages=find_packages(include=['antconnect', 'antconnect.*']),
    
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,

    install_requires=requires,
    dependency_links=links,

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)


if overlay_warning:
    sys.stderr.write("""
========
WARNING!
========
You have just installed ant over top of an existing installation, without removing it first. 
Because of this, your install may now include extraneous files from a previous version that have since been removed from ant. This is known to cause a variety of problems. You should manually remove the
%(existing_path)s
directory and re-install ant.
""" % {"existing_path": existing_path})
