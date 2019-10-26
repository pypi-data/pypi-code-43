import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


metadata_path = "datamaker/common/metadata/"
static_path = "datamaker/common/static/"
datafiles = [
    ("metadata", [metadata_path + "formats.json"]),
    ("metadata", [metadata_path + "parameters.json"]),
    ("static", [static_path + "cities.json"]),
    ("static", [static_path + "countries.json"]),
    ("static", [static_path + "names.json"]),
    ("static", [static_path + "states.json"]),
    ("static", [static_path + "streets.json"]),
]


setuptools.setup(
    name="datamaker",
    version="0.1.1",
    author="Alex Broley",
    author_email="alex.broley@gmail.com",
    description="A package for generating tabluar datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tekkabroley/DataMaker",
    packages=setuptools.find_packages(),
    data_files=datafiles,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    include_package_data=True
)
