"""Setup module."""
from distutils.core import setup

setup(
    name='falcontyping',
    version='0.1.0',
    url='https://github.com/abdelrahman-t/falcontyping',
    author='Abdurrahman Talaat <abdurrahman.talaat@gmail.com>',
    author_email='abdurrahman.talaat@gmail.com',
    packages=['falcontyping', 'falcontyping.base', 'falcontyping.middleware', 'falcontyping.typedjson'],
    include_package_data=True,
    python_requires='>=3.7.0',
    install_requires=['falcon'],

    keywords=['falcon', 'typing', 'hints', 'mypy', 'pydantic', 'marshmallow'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.7',
    ],
)
