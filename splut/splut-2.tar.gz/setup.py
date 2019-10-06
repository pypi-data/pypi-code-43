import setuptools

setuptools.setup(
        name = 'splut',
        version = '2',
        description = 'Concurrency-related Python utils',
        install_requires = [],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['bg', 'delay'],
        scripts = [])
