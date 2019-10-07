import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'outjack',
        version = '5',
        description = 'JACK integration for Python',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/outjack',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = [],
        install_requires = ['cython', 'nativecommon'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
