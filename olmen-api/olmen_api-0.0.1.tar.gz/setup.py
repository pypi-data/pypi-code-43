import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="olmen_api",
    use_scm_version=True,
    setup_requires=['setuptools_scm'],
    author="Max Zhao",
    author_email="max.zhao@charite.de",
    description="Scrape olmen to get questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xiamaz/olmen_api",
    py_modules=["olmen_api"],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
