import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='zerocrypt',
    version='0.2',
    author="Zerolevel team",
    author_email="zerolevel@gmail.com",
    description="Node' crypto library bind to python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    #Update
    packages=['zerocrypt'],
    package_data={'zerocrypt': [
        'libcrypto.dylib',
        'libcrypto.so',
        'libcrypto.dll',
    ]},

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)