import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'timelyOSC',
        version = '3',
        description = 'Open Sound Control library for Python 3',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/timelyOSC',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['timelyOSC'],
        install_requires = [],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
