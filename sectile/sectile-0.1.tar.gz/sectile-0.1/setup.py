from setuptools import find_packages, setup


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='sectile',
    version='0.1',

    description='Multidimensional file stitcher',
    long_description=long_description,
    long_description_content_type="text/markdown",

    license='MIT',
    url='https://github.com/norm/sectile',
    author='Mark Norman Francis',
    author_email='norm@201created.com',

    install_requires=[
        'toml',
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: General',
    ]
)
