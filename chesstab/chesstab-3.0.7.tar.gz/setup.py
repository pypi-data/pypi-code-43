# setup.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

from setuptools import setup

if __name__ == '__main__':

    long_description = open('README').read()

    setup(
        name='chesstab',
        version='3.0.7',
        description='Database for chess games',
        author='Roger Marsh',
        author_email='roger.marsh@solentware.co.uk',
        url='http://www.solentware.co.uk',
        package_dir={'chesstab':''},
        packages=[
            'chesstab',
            'chesstab.core', 'chesstab.basecore', 'chesstab.gui',
            'chesstab.help',
            'chesstab.db', 'chesstab.dpt', 'chesstab.sqlite', 'chesstab.apsw',
            'chesstab.fonts',
            'chesstab.about',
            ],
        package_data={
            'chesstab.about': ['LICENCE', 'CONTACT'],
            'chesstab.fonts': ['*.TTF', '*.zip'],
            'chesstab.help': ['*.rst', '*.html'],
            },
        long_description=long_description,
        license='BSD',
        classifiers=[
            'License :: OSI Approved :: BSD License',
            'Programming Language :: Python :: 3.6',
            'Operating System :: OS Independent',
            'Topic :: Games/Entertainment :: Board Games',
            'Intended Audience :: End Users/Desktop',
            'Development Status :: 4 - Beta',
            ],
        install_requires=[
            'solentware-base==3.0.1',
            'chessql==1.1.4',
            'solentware-grid==1.2',
            'pgn-read==1.2.4',
            'solentware-misc==1.1.1',
            'uci-net==1.1.1',
            ],
        dependency_links=[
            'http://solentware.co.uk/files/solentware-base-3.0.1.tar.gz',
            'http://solentware.co.uk/files/chessql-1.1.4.tar.gz',
            'http://solentware.co.uk/files/solentware-grid-1.2.tar.gz',
            'http://solentware.co.uk/files/pgn-read-1.2.4.tar.gz',
            'http://solentware.co.uk/files/solentware-misc-1.1.1.tar.gz',
            'http://solentware.co.uk/files/uci-net-1.1.1.tar.gz',
            ],
        )
