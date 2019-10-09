import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()



setuptools.setup(
    name="canvas-lms-api",
    version="0.1.6",
    author="Tyson Bailey",
    author_email="tyson@onaclovtech.com",
    description="Pip installable canvas API used by GT classes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.gatech.edu/omscs-ta/canvas_lms_api",
#    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests"],
    python_requires='>=3.6',
    packages=["canvas_lms_api"]
)
    
