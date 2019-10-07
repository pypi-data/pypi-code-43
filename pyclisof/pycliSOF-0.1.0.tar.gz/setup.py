from distutils.core import setup

setup(
    name='pycliSOF',
    version='0.1.0',
    author='Harshit Babbar',
    author_email='harshitbabbar968@gmail.com',
    packages=['pystack'],
    scripts=['pystack/stack-bash.py'],
    url='http://pypi.python.org/pypi/pycliSOF/',
    license='LICENSE.txt',
    description='bash stack script',
    long_description=open('README.txt').read(),
    install_requires=[
        "bs4 == 0.0.1",
        "requests == 2.2.1",
	"colorama"=="0.2.5",
	"texttable"=="1.6.2",
    ],
)
