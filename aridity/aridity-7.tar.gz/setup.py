import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'aridity',
        version = '7',
        description = 'DRY config and template system',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/aridity',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['aridity', 'arid_config'],
        install_requires = ['pyparsing'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = ['aridity.py', 'arid-config'])
