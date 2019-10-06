import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="lambert",
    version="1.0.0",
    description="Convert location units from WS84 to Lambert (I,II,III) and reverse",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/willena/lambert-python",
    author="Willena",
    author_email="contact@guillaumevillena.fr",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["lambert"],
    include_package_data=True,
    install_requires=[],
    # entry_points={
    #     "console_scripts": [
    #         "realpython=lambert.__main__:main",
    #     ]
    # },
)