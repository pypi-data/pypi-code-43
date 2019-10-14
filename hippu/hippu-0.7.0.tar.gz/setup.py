import os
from setuptools import setup, find_packages

module_name = 'hippu'

meta = {}
with open(os.path.join(os.path.dirname(__file__),
                       'src', module_name, '_meta.py'), 'rt') as f:
    exec(f.read(), meta)  # pylint: disable=exec-used


setup(
    name=module_name,
    version=meta['__version__'],
    description='Hippu - Micro HTTP Server',
    url='https://gitlab.com/slaine/{}.git/'.format(module_name),
    author=meta['__author__'],
    author_email='sami.jy.laine@gmail.com',
    entry_points={},
    license=meta['__license__'],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    zip_safe=False,
    include_package_data=True,  # Defined in MANIFEST.in
    # 'install_requires' should be used to specify what a project minimally
    # needs to run correctly. When the project is installed by pip, this is
    # the specification that is used to install its dependencies.
    #
    # Python Packaging User Guide:
    #   https://setuptools.readthedocs.io/en/latest/setuptools.html?highlight=install_requires#id17
    #   https://packaging.python.org/discussions/install-requires-vs-requirements/
    install_requires=[
    ],
    extras_require={
        # 'test': ['pytest'],
    },
)
