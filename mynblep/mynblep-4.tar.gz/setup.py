import setuptools

setuptools.setup(
        name = 'mynblep',
        version = '4',
        description = 'MinBLEPs library including fast naive waveform conversion',
        install_requires = ['numpy', 'pyrbo'],
        packages = setuptools.find_packages(),
        package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
        py_modules = [],
        scripts = [])
