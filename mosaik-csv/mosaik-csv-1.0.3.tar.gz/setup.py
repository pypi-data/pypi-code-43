from setuptools import setup


setup(
    name='mosaik-csv',
    version='1.0.3',
    author='Stefan Scherfke',
    author_email='mosaik@offis.de',
    description=('Presents CSV datasets to mosaik as models.'),
    long_description=(open('README.rst').read() + '\n\n' +
                      open('CHANGES.txt').read() + '\n\n' +
                      open('AUTHORS.txt').read()),
    url='https://bitbucket.org/mosaik/mosaik-csv',
    py_modules=['mosaik_csv'],
    install_requires=[
        'arrow>=0.9.0',
        'mosaik-api>=2.0',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mosaik-csv = mosaik_csv.mosaik:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering',
    ],
)
