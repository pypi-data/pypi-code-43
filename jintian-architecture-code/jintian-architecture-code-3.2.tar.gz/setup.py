import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jintian-architecture-code",
    version="3.2",
    author="",
    author_email="767980702@qq.com",
    description="jintian-architecture-code",
    long_description=long_description,
    long_description_content_type="",
    url="",
    packages=['com/fw/base', 'com/fw/db', 'com/fw/system', 'com/fw/utils'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
