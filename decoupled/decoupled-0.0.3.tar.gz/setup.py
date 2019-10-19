import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
        name="decoupled",
        version="0.0.3",
        author="Sören Glimm",
        author_email="git@uncleowen.de",
        description="Run a python function (e.g., a test) in it's own process",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://gitlab.com/UncleOwen/decoupled",
        packages=setuptools.find_packages(),
        install_requires=['decorator'],
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Development Status :: 3 - Alpha",
        ],
)
