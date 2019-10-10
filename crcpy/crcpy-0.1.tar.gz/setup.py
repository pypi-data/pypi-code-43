import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='crcpy',
    version='0.1',
    author="Zerolevel team",
    author_email="zerolevel@gmail.com",
    description="Node' crc32sum library bind to python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    #Update
    packages=['crcpy'],
    package_data={'crcpy': [
        'libcrclib.dylib',
        'libcrclib.so',
        'libcrclib.dll',
    ]},

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)