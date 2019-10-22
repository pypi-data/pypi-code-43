import setuptools
from os.path import join, dirname

import medicine_utils

setuptools.setup(
    name='medicine-utils',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        'templates': ['*']
    },
    version=medicine_utils.__version__,
    license='MIT',
    url='https://bitbucket.org/med-logic/medicine-utils',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    long_description_content_type="text/markdown"
)
