import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wagtail_site_of_Alexandro.by",
    version="2.0.1",
    author="Alexandro.by",
    author_email="alexander.ermak@celadon.ae",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/Alexandro11by/deploy_wagtail_using_ansible",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)