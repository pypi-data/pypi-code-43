from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='tail_uwsgi_log',
    version='0.0.2',
    packages=find_packages(),

    install_requires=['yagmail>=0.11.220'],

    author='Kant',
    author_email='kant@kantli.com',

    description='Tail several uwsgi log files and send an email when error occurs.',
    long_description=long_description,
    keywords='uwsgi log',
    url='https://github.com/kant-li/uwsgi_log_analysis',
    license='MIT License',

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',

    entry_points={
        "console_scripts": [
            "tail_uwsgi_log = tail_uwsgi_log.monitor:tail_uwsgi_log",
        ]
    },
)
