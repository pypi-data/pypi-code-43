import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="DialogFlowPy",
    version="0.1",
    author="Mayank Beri",
    author_email="mayank@logicfactory.com.au",
    description="A Python Library to interface with Dialogflow",
    long_description="A Python Library to interface with Dialogflow",
    long_description_content_type="text/markdown",
    url="https://github.com/mayankberi1/DialogFlowPy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)