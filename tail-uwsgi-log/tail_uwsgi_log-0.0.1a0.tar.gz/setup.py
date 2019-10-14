from setuptools import setup, find_packages

setup(
    name='tail_uwsgi_log',
    version='0.0.1a',
    packages=find_packages(),

    install_requires=['yagmail>=0.11.220'],

    author='Kant',
    author_email='kant@kantli.com',

    description='Tail several uwsgi log files and send an email when error occurs.',
    keywords='uwsgi log',
    url='https://github.com/kant-li/uwsgi_log_analysis',
    license='MIT License',

    entry_points={
        "console_scripts": [
            "tail_uwsgi_log = tail_uwsgi_log.monitor:tail_uwsgi_log"
        ]
    },
)
