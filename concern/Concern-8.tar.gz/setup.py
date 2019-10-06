import setuptools

setuptools.setup(
        name = 'Concern',
        version = '8',
        description = 'Control FoxDot or pym2149 using Vim',
        install_requires = ['aridity', 'lagoon', 'timelyOSC', 'pyven'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = [],
        scripts = ['Concern'])
