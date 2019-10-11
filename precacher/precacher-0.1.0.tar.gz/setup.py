from setuptools import setup

setup(
    name='precacher',
    python_requires='>=3.6.0',
    version='0.1.0',
    packages=['precacher'],
    install_requires=['dnspython>=1.16'],
    entry_points={
        'console_scripts': [
            "precacher=precacher.__main__:main",
        ]
    },
    url='https://github.com/dcoker/precacher/',
    license='https://www.apache.org/licenses/LICENSE-2.0',
    author='Doug Coker',
    author_email='dcoker@gmail.com',
    description='Replays DNS queries from Pi-hole or dnscrypt-proxy.'
)
