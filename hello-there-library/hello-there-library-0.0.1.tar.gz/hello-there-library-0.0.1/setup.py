from setuptools import find_packages, setup

setup(
    name = 'hello-there-library',
    version = '0.0.1',
    package = find_packages,
    include_package_data = True,
    package_dir = {'': '.'},
    description = "Say hello there lib"
)
