import setuptools

long_description = "A python judging client library for Cosmos front-ends"

setuptools.setup(
    name='pycosmos',
    version='0.11',
    author="Chinmay Phulse",
    author_email="phulsechinmay@gmail.com",
    packages=['pycosmos'],
    description="A python judging client library for Cosmos front-ends",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/phulsechinmay/pycosmos",
    download_url = 'https://github.com/phulsechinmay/pycosmos/archive/v_011.tar.gz',
    install_requires=[
        'requests',
        'pandas',
        'numpy'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
