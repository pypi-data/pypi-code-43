import setuptools

setuptools.setup(
        name = 'timelyOSC',
        version = '2',
        description = 'Open Sound Control library for Python 3',
        install_requires = [],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['timelyOSC'],
        scripts = [])
