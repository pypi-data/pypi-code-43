import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'nativecommon',
        version = '3',
        description = 'Common code of projects with native parts',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/nativecommon',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['initnative'],
        install_requires = [],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
