from setuptools import setup, find_packages

setup(
    name='wf-database-connection',
    packages=find_packages(),
    version='0.1.0',
    include_package_data=True,
    description='A simple, generic database interface that can be adapted to many different use cases and implementations',
    long_description=open('README.md').read(),
    url='https://github.com/WildflowerSchools/database_connection',
    author='Theodore Quinn',
    author_email='ted.quinn@wildflowerschools.org',
    install_requires=[
        'python-dateutil>=2.8.0'
    ],
    keywords=['database'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
