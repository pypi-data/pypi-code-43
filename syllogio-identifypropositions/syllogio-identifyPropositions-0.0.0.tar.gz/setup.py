from setuptools import setup, find_packages
from identifyPropositions import __version__

setup(
    name="syllogio-identifyPropositions",
    version=__version__,
    url="https://github.com/syllogio/syllogio-identifyPropositions",
    license="MIT",
    author="Peter Sieg",
    author_email="chasingmaxwell@gmail.com",
    description="Identify natural language propositions in a written argument.",
    packages=find_packages(exclude=["tests"]),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "identifyPropositions = identifyPropositions.__main__:main",
            "idpr = identifyPropositions.__main__:main",
        ]
    },
)
