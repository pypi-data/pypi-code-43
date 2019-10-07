import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gsclight",
    version="0.0.1",
    author="Gunnar Griese",
    author_email="gugriese.gg@gmail.com",
    description="A simplified package for Google Search Console API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GunnarGriese/google-search-console",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)