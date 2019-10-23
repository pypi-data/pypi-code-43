import setuptools
from whatcha_readin.config import VERSION

setuptools.setup(
    name="whatcha-readin",
    url="https://github.com/allisonking/whatcha-readin",
    author="Allison King",
    author_email="allisonjuliaking@gmail.com",
    classifers=["Programming Language :: Python :: 3.7"],
    license="MIT ",
    python_requires=">=3.6",
    version=VERSION,
    description="githook for adding currently reading books to git commit messages",
    packages=setuptools.find_packages(),
    entry_points={"console_scripts": ["whatcha-readin=whatcha_readin.cli:cli"]},
    install_requires=[
        "certifi",
        "chardet",
        "Click",
        "configparser",
        "idna",
        "requests",
        "urllib3",
        "xmltodict",
    ],
)
