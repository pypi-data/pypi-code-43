# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='xtream',
    version='0.5.1',
    description='nstream streaming platform',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(),
    author='Vladmir Impala',
    author_email='your@email.com',
    keywords=['NStream', 'IPTV Platform', 'Streaming Platform'],
    url='https://github.com/xtream/xtream',
    download_url='https://pypi.org/project/xtream/',
    namespace_packages=[],
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'nstream = xtream.main:main'
        ]
    },
)

install_requires = [
        "cliff",
        "requests",
        "docopt",
        "requests",
        "django",
        "pytest",
        "py-cpuinfo",
        "celery",
        "redis",
        "dj-static",
        "static3",
        "gunicorn",
        "django-heroku",
        "uWSGI",
        "django-ratelimit",
        "django-crispy-forms",
        "iso8601"       
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)