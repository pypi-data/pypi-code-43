from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()


setup(
    name='itime',
    description='Awesome time format converter',
    version='0.0.4',
    author='Shelwin Xiao',
    author_email='shliangxiao@gmail.com',
    url='https://github.com/slxiao/itime',
    license='Public Domain',
    keywords=['time', 'format', 'converter'],
    install_requires=['pytz>=2018.7'],
    package_dir={'':'src'},
    py_modules=['itime'],
    setup_requires=['pytz>=2018.7'],
    classifiers=[
        'Programming Language :: Python',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent'
    ],
)