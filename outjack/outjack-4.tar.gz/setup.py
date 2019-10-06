import setuptools

setuptools.setup(
        name = 'outjack',
        version = '4',
        description = 'JACK integration for Python',
        install_requires = ['cython', 'nativecommon'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = [],
        scripts = [])
