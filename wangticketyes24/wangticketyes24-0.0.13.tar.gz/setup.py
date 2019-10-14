import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wangticketyes24",
    version="0.0.13",
    author="Wangticket",
    author_email="wangticket77@gmail.com",
    description="wangticket for y",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/Wangticket/",
    packages=['wangticketyes24'],
    install_requires=['beautifulsoup4', 'selenium', 'requests'],
    python_requires='>=3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
