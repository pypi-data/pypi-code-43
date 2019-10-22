import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='docx2python-kryon',
    version='1.0.1',
    author="Fabian Gröger",
    author_email="fabian.groeger@bluein.ch",
    description="Extract content from docx files. Edited for Kryon Studio (RPA).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/FabianGroeger96/docx2python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)



