import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="target365_sdk",
    version="1.3.3",
    author="Target365",
    author_email="support@target365.no",
    description="Target365 SDK",
    long_description="Enables integration with Target365 online services.",
    long_description_content_type="text/markdown",
    url="https://github.com/Target365/sdk-for-python",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests',
          'ecdsa',
          'jsonpickle',
      ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',        
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
