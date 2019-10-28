from setuptools import setup, find_packages

setup(
    name='integration-cli',
    version='2.5.4',
    packages=find_packages(),
    py_modules=['cli', 'helpers', 'utils', '/files', '_default_settings', '_default_urls', '_default_wsgi'],
    install_requires=[
        'Click>=5.1',
        'djangorestframework==3.8.2',
        'Django==2.0.7',
        'psycopg2-binary==2.7.4',
    ],
    entry_points="""
        [console_scripts]
        integration=cli:cli
    """,
    include_package_data=True,
)
