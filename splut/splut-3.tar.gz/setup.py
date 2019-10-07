import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'splut',
        version = '3',
        description = 'Concurrency-related Python utils',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/splut',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['bg', 'delay'],
        install_requires = [],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
