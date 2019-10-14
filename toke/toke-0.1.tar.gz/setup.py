from setuptools import setup

setup(
    name='toke',
    version='0.1',
    author='keaising',
    author_email='keaising@gmail.com',
    description='Tool Of KEaising',
    url="https://github.com/keaising/toke",
    py_modules=['toke'],
    install_requires=[
        'Click',
        'python-dotenv'
        'tweepy'
    ],
    entry_points='''
        [console_scripts]
        toke=toke:cli
    ''',
)