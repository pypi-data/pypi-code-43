import resumableds

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="resumableds",
    version=resumableds.__version__,
    author=resumableds.__author__,
    author_email=resumableds.__author_email__,
    description="A Python class that supports Data Science projects.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/systemverwalter/resumableds",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Jupyter",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Utilities",
                ],
)
