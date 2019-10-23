import setuptools
import os


buildversion = os.environ.get('BUILD_VERSION', '0.0').split('-')[0]

if __name__ == '__main__':
    with open('README.md', 'r') as fh:
        long_description = fh.read()

    setuptools.setup(
        name='protocolinterface',
        version=buildversion,
        author='Acellera',
        author_email='info@acellera.com',
        description='ProtocolInterface: A class to make python classes validate arguments.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/acellera/protocolinterface/',
        classifiers=[
            'Programming Language :: Python :: 3.6',
            'Operating System :: POSIX :: Linux',
        ],

        packages=setuptools.find_packages(include=['protocolinterface*'], exclude=[]),

        install_requires=[]
    )