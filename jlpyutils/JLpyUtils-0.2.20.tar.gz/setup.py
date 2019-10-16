import setuptools
from distutils.version import LooseVersion
from pathlib import Path
import os
import re
import codecs

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_requirements(requirements='requirements.txt'):
    """Get the list of requirements from the pip `requirements` file.
    Args:
        requirements (str): path to the pip requirements file.
    Examples:
        ['django==1.5.1', 'mezzanine==1.4.6']
    Returns:
        List[str]: the list of requirements
    """
    # pip v1.5 started requiring the 'session'
    # pip v10.0.0 moved these wonderful methods to ._internal. Boo!
    from pip import __version__ as pip_version
    if LooseVersion(pip_version) < LooseVersion('1.5'):
        from pip.req import parse_requirements
        do_parse = lambda path: parse_requirements(path)  # noqa: E731
    elif LooseVersion(pip_version) < LooseVersion('10.0.0'):
        from pip.req import parse_requirements
        from pip.download import PipSession
        do_parse = lambda path: parse_requirements(path, session=PipSession())  # noqa: E731
    else:
        # We're in the bold new future of using internals... yeah
        from pip._internal.req import parse_requirements
        from pip._internal.download import PipSession
        do_parse = lambda path: parse_requirements(path, session=PipSession())  # noqa: E731
    # Cool trick to automatically pull in install_requires values directly from
    # your requirements.txt file but you need to have pip module available
    install_reqs = do_parse(os.path.join(here, requirements))
    return [str(ir.req) for ir in install_reqs]

def _determine_requirements_txt_location():
    this_dir = Path(__file__).parent
    if Path(this_dir, 'requirements.txt').exists():
        return 'requirements.txt'
    elif Path(this_dir, 'JLpyUtils.egg-info', 'requires.txt').exists():
        return 'JLpyUtils.egg-info/requires.txt'
    else:
        raise FileExistsError('Unable to find a requirements.txt file')

#define directories to exclude from setup
exclude_dirs = ['ez_setup', 'examples', 'tests', 'venv']
        
# fetch long description from readme
with open("README.md", "r") as fh:
    README = fh.read()
    
#fetch scripts
try:
    scripts = ['scripts/%s' % f for f in os.listdir('scripts') if f != "dummy.py"]
except OSError:
    scripts = []
    
setuptools.setup(
    name = 'JLpyUtils',
    version= find_version('JLpyUtils', '__init__.py'),
    author="John T. Leonard",
    author_email="jtleona01@gmail.com",
    description='General utilities to streamline data science and machine learning routines in python',
    long_description= README,
    long_description_content_type="text/markdown",
    url="https://github.com/jlnerd/JLpyUtils.git",
    packages= setuptools.find_packages(exclude=exclude_dirs),
    include_package_data=True,
    scripts=scripts,
    setup_requires=["pep8", "setuptools>=30"],
    dependency_links=[],
    #test_suite='ci_scripts.run_nose.run',
    #tests_require=['nose>=1.3.7', 'coverage'],
    zip_safe=False,
    install_requires=get_requirements(_determine_requirements_txt_location()),
    entry_points={},
)

