import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ResifDataTransferTransaction",
    version="0.1.1",
    author="RESIF",
    author_email="resif-dc@univ-grenoble-alpes.fr",
    description="Create, parse, modify an XML file associated to a transaction.",
    long_description="Create, parse, modify an XML file associated to a transaction.",
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': ['ResifDataTransferTransaction=ResifDataTransferTransaction.Transaction:main']
    },
    url='https://gitlab.com/resif',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
