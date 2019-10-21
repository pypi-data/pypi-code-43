"""
pipdeps setup
"""
from setuptools import setup, find_packages

setup(
    name='pipdeps',

    description='Pipdeps shows/upgrades outdated packages with respect to existing \
                     dependencies.',
    classifiers=[
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    author='IT4Innovations',
    author_email='support@it4i.cz',
    url='https://code.it4i.cz/sccs/pip-deps',
    license='GPLv3+',
    packages=find_packages(),
    namespace_packages=['pipdeps'],
    include_package_data=True,
    zip_safe=False,
    version_format='{tag}',
    long_description_markdown_filename='README.md',
    setup_requires=['mustache', 'pystache', 'setuptools-git-version', 'setuptools-markdown'],
    install_requires=[
        'packaging',
        'tabulate',
        'wheel',
    ],
    entry_points={
        'console_scripts': [
            'pipdeps = pipdeps.pipdeps:main',
        ]
    }
)
