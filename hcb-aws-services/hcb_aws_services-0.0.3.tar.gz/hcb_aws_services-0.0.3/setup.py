import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hcb_aws_services",
    version="0.0.3",
    author="Zachary R. Bannor",
    author_email="zachary.bannor@spr.com",
    description="A package containing functions to use aws boto3",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.infutor.com/high-capacity-batch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'python>=3.7',
        'boto3']
)