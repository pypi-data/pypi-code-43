import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pynhl",
    version="0.1.8",
    author="Jay Lowenthal",
    author_email="jasonlowenthal@live.com",
    description="Python wrapper for NHL API used in Home Assistant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/JayBlackedOut/pynhl",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
