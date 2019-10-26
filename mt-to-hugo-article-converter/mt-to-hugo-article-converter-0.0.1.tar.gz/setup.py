import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mt-to-hugo-article-converter",
    version="0.0.1",
    author="Hidenori MATSUKI",
    author_email="dev@mazgi.com",
    description="Convert articles from MT to Hugo",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mazgi/mt-to-hugo-article-converter",
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=[
        "python-dateutil",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Text Processing",
    ],
    python_requires='>=3.6',
)
