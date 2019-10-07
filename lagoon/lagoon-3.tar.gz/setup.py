import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'lagoon',
        version = '3',
        description = 'Experimental layer on top of subprocess',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/lagoon',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['screen', 'lagoon'],
        install_requires = [],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
