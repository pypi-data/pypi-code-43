import sys
from pathlib import Path
from setuptools import setup, find_packages

if not sys.version_info >= (3, 6):
    raise RuntimeError('ignot requires at least python 3.6')

readme = Path('README.rst').read_text()
history = Path('HISTORY.rst').read_text()

requirements = Path('requirements.txt').read_text().splitlines()
setup_requirements = []
test_requirements = Path('requirements_dev.txt').read_text().splitlines()

setup(
    author='Andriy Kushnir (Orhideous)',
    author_email='me@orhideous.name',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description='Simple CLI for MC versions management',
    install_requires=requirements,
    license='MIT license',
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['Minecraft', 'modpack', 'skcraft'],
    name='ignot',
    packages=find_packages(include=['ignot']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://git.mc4ep.org/mc4ep/ignot',
    version='0.1.0',
    zip_safe=False,
    entry_points='''
        [console_scripts]
        ignite=ignot.cli:cli
    ''',
)
