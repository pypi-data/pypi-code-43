import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="contentmatcher",
    version="0.0.1",
    author="Brandon M. Pace",
    author_email="brandonmpace@gmail.com",
    description="A pattern-based content matcher for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="content pattern matcher",
    license="GNU Lesser General Public License v3 or later",
    platforms=['any'],
    python_requires=">=3.6.5",
    url="https://github.com/brandonmpace/contentmatcher",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3"
    ]
)
