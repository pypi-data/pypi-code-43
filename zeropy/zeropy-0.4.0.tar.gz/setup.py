import setuptools

try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except OSError as err:
    print(err)

setuptools.setup(
    name='zeropy',
    version='0.4.0',
    author="zerolevel team",
    author_email="zerolevel@gmail.com",
    description="zerolevel blockchain's api bind.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=['zerocrypt==0.2', 'crcpy==0.1'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved",
        "Operating System :: OS Independent",
    ],
)
