import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="importFromParent",
    version=input('Type the version (to upload = "0.0.4"): '),
    author="Cauã S. C. P.",
    author_email="cauascp37@gmail.com",
    description="import a package or a module from a py file's parent.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.youtube.com/channel/UCAbwAklWIeuoKKjVBMQVCew",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
