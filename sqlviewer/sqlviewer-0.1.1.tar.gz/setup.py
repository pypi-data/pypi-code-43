import os
from setuptools import setup

requires = [
    "betterpy",
    "psycopg2"
]

# Write hierachy
ensure = lambda path, method: not os.path.exists(path) and method(path)

directory = os.path.join(os.path.expanduser('~'), '.pysql')
ensure(directory, os.mkdir)
ensure(os.path.join(directory, 'history'), os.mkdir)
ensure(os.path.join(directory, 'master.ini'), lambda x: open(x, 'a').close())
ensure(os.path.join(directory, 'master.hist'), lambda x: open(x, 'a').close())

setup(
    name='sqlviewer',
    install_requires=requires,
    version="0.1.1",
    description="Basic cli sql viewer for databases - intended to allow for quick sanity checks",

    author="Kieran Bacon",
    author_email="kieran.bacon@outlook.com",

    packages=['sqlviewer'],

    entry_points={
        'console_scripts': [
            'sql = sqlviewer.viewer:main',
        ],
        'sqlviewer_connectors': [
            'sqlite = sqlviewer.connector:SQLiteConnector',
            'postgres = sqlviewer.connector:PostgresConnector'
        ]
    }
)