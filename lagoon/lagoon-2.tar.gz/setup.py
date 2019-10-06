import setuptools

setuptools.setup(
        name = 'lagoon',
        version = '2',
        description = 'Experimental layer on top of subprocess',
        install_requires = [],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = ['screen', 'lagoon'],
        scripts = [])
