import setuptools

with open("README.md") as readme_file:
    readme = readme_file.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    author="Nicholas Wolf",
    author_email="nwolf@noao.edu",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A light-weight client for receiving alerts from ANTARES.",
    entry_points={"console_scripts": ["antares=antares_client.cli:entry_point"]},
    install_requires=requirements,
    long_description=readme,
    long_description_content_type="text/markdown",
    name="antares-client",
    packages=setuptools.find_packages(),
    setup_requires=["nose>1.0"],
    python_requires=">=3.4",
    url="https://github.com/cstubens/antares_client",
    version="v0.3.1",
)
