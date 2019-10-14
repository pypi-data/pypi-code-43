from setuptools import setup, find_packages
from flipexception import flipexception

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = ''

VERSION = str(flipexception.__version__)

setup(
    name='FlipException',
    version=VERSION,
    license='Mozilla Public License',
    author='Jesus Roldan',
    author_email='jesus.roldan@gmail.com',
    description="The best way to flip an exception out of rage",
    long_description=long_description,
    url='https://github.com/xeBuz/FlipException',
    packages=find_packages(),
    platforms='any',
    test_suite='nose.collector',
    install_requires=[
        'upsidedown==0.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: User Interfaces',
        'Topic :: Terminals',
    ]
)
