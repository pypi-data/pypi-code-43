import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="blcv",
    version="0.1.0",
    author="Xinyue Wei",
    author_email="sarahwei0210@gmail.com",
    description="tools for using Blender for cv",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SarahWeiii/Blender_cv.git",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)