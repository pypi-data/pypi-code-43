import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'Concern',
        version = '9',
        description = 'Control FoxDot or pym2149 using Vim',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/Concern',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = [],
        install_requires = ['aridity', 'lagoon', 'timelyOSC', 'pyven'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = ['Concern'])
