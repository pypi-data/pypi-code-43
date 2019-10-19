import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="template-nest",
    version="1.0.0",
    description="Represent a nested structure of templates in a dict",
    long_description=README,
    long_description_content_type="text/markdown",
    author="Tom Gracey",
    author_email="tomgracey@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["template_nest"],
    include_package_data=True,
    install_requires=["os", "re", "json", "unittest" ]
)

