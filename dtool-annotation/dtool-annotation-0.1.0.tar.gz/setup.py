from setuptools import setup

url = "https://github.com/jic-dtool/dtool-annotation"
version = "0.1.0"
readme = open('README.rst').read()

setup(
    name="dtool-annotation",
    packages=["dtool_annotation"],
    version=version,
    description="Add ability to annotate datasets using the dtool CLI",
    long_description=readme,
    include_package_data=True,
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
    url=url,
    install_requires=[
        "click",
        "dtoolcore>=3.13.0",
        "dtool-cli",
    ],
    entry_points={
        "dtool.cli": [
            "annotation=dtool_annotation.cli:annotation",
        ],
    },
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
