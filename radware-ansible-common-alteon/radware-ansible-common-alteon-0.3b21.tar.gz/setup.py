from setuptools import setup
import os


current = os.path.abspath(os.path.dirname(__file__))
os.chdir(current)

about = {}
with open(os.path.join(current, 'ansible', '__init__.py'), 'r') as f:
    exec(f.read(), about)

with open('README.md', 'r') as f:
    readme = f.read()

with open('requirements.txt') as fh:
    required = [x for x in fh.read().splitlines() if not x.startswith('#')]

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=['ansible.module_utils.network.radware', 'ansible.modules.network.radware'],
    install_requires=required,
    url=about['__url__'],
    keywords=['radware', 'ansible', 'alteon', 'common'],
    license=about['__license__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    python_requires='~=3.6',
    data_files=[('.', ['requirements.txt'])],
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers'
    ]
)

