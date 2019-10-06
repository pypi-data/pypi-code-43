import setuptools

setuptools.setup(
        name = 'nativecommon',
        version = '2',
        description = 'Common code of projects with native parts',
        install_requires = [],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['initnative'],
        scripts = [])
