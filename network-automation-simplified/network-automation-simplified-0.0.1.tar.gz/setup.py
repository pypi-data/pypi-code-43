from sys import platform
from setuptools import setup
from os import mkdir, chmod, path
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg

with open(path.join("./", 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

class OverrideInstall(_bdist_egg):

    def run(self):
        '''
        addtional functions to perform in addtion 
        to the standard installation.  *only when
        'python setup.py is used
        '''

        pass
        _bdist_egg.run(self)

setup(
    name='network-automation-simplified',
    version='0.0.1',
    description='Network Automation Simplified',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    author='Cox Communications Inc.',
    author_email='jason.cole@cox.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: System :: Networking',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='ncclient, nornir, jsnapy',
    packages=["nams"],
    package_dir={"nams": "src/nams"},
    python_requires='>=3.7',
    install_requires=["jsnapy","xmltodict","nornir","recordclass"],
    cmdclass={"bdist_egg": OverrideInstall},
)
