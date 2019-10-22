from setuptools import setup, find_packages

LONGDESC = """Sends text messages to a pre-configured telegram chat.  Useful to
send notifications from background or long-running processes.  Very simple to
use.
"""

setup(
    name='telega_notify',
    version='0.1',
    description='Send messages to a Telegram chat',
    author='Justin Forest',
    author_email='hex@umonkey.net',
    url='http://github.com/umonkey/telega-notify',
    packages=find_packages(),
    install_requires=[],
    long_description=LONGDESC,
    license='GNU GPL',

    entry_points={
        'console_scripts': [
            'telega = telega_notify.main:main'
        ]
    },

    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)
