import setuptools

setuptools.setup(
        name = 'aridity',
        version = '6',
        description = 'DRY config and template system',
        install_requires = ['pyparsing'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['aridity', 'arid_config'],
        scripts = ['aridity.py', 'arid-config'])
