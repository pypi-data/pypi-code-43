import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lofter_utils",
    version="0.1.4",
    author="Hawthorn2013",
    author_email="hawthorn7dd@hotmail.com",
    description="Lofter utils support download and convert danmu.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hawthorn2013/lofter_utils",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': ['lofterutils=lofter_utils.CmdInterface:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)