from setuptools import setup
setup(
    name='pyvirtualname',
    version='0.1.2',
    description='Wrapper for Virtualname API',
    url='https://gitlab.com/carbans/pyvirtualname',
    author='Carlos Latorre',
    author_email='me@carloslatorre.net',
    license='GPL3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3'
    ],
    packages=['pyvirtualname'],
    install_requires=[
          'requests'
    ],
)

