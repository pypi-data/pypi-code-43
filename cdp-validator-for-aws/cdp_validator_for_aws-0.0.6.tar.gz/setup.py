import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cdp_validator_for_aws",
    version="0.0.6",
    description="Validation of aws resources used to create Cloudera Data Platform environments",
    install_requires=['boto3>=1.9.242'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    package_data={'cdp_validator_for_aws': ["policies/*.json"]},
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
