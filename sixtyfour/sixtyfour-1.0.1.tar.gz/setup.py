from setuptools import setup


setup(
    name='sixtyfour',
    version='1.0.1',
    packages=['sixtyfour'],
    author='Kevin Kennell',
    author_email='kevin@kennell.de',
    license='MIT',
    url='https://github.com/kennell/sixtyfour',
    install_requires=[
        'click'
    ],
    entry_points={
        'console_scripts': [
            'sixtyfour = sixtyfour.cli:main'
        ]
    }
)
