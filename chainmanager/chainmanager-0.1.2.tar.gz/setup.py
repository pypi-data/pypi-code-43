from io import open
from setuptools import setup
from chainmanager import __version__ as version

setup(
    name='chainmanager',
    version=version,
    url='https://github.com/manso92/chain-manager',
    license='MIT',
    author='Pablo Manso',
    author_email='92manso@gmail.com',
    description='Manages all the chains of a projects and inserts them into de gestor.',
    long_description=''.join(open('README.md', encoding='utf-8').readlines()),
    long_description_content_type='text/markdown',
    keywords=['gui', 'executable'],
    packages=['chainmanager'],
    include_package_data=True,
    install_requires=['Eel==0.10.4',
                      'selenium',
                      'pandas',
                      'numpy',
                      'pathlib',
                      'numpy',
                      'xlrd'],
    python_requires='>=3.6',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux'
    ],
    entry_points={
        'console_scripts': [
            'chainmanager=chainmanager.__main__:run'
        ]
    }
)
