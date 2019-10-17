import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.pypi.md").read_text()

setup(
    name="crawling-gocd",
    version="1.0.1",
    description="crawling the gocd build histories of pipelines and calculate the metrics",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/play-code-tools/crawling-gocd",
    author="play-code-tools",
    author_email="ellendan000@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=("tests",)),
    install_requires=["requests-html", "pyyaml", "pyfunctional"],
    entry_points={
        "console_scripts": [
            "realpython=crawling_gocd.__main__:main",
        ]
    },
)