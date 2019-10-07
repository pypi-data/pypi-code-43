import setuptools

def long_description():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
        name = 'pyrbo',
        version = '3',
        description = 'Python JIT compiler for near-native performance of low-level arithmetic',
        long_description = long_description(),
        long_description_content_type = 'text/markdown',
        url = 'https://github.com/combatopera/pyrbo',
        author = 'Andrzej Cichocki',
        packages = setuptools.find_packages(),
        py_modules = ['pyrbo'],
        install_requires = ['numpy', 'cython', 'nativecommon'],
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        scripts = [])
