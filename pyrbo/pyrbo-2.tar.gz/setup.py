import setuptools

setuptools.setup(
        name = 'pyrbo',
        version = '2',
        description = 'Python JIT compiler for near-native performance of low-level arithmetic',
        install_requires = ['numpy', 'cython', 'nativecommon'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['pyrbo'],
        scripts = [])
