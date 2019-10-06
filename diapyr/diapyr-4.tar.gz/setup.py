import setuptools

setuptools.setup(
        name = 'diapyr',
        version = '4',
        description = 'Constructor injection for Python',
        install_requires = [],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = [],
        scripts = [])
