import setuptools

with open("requirements.txt", "r") as requirements_file:
    requirements = requirements_file.read()

setuptools.setup(
    name="burpsuite",
    version="0.0.1",
    author="Julian Nash",
    author_email="julian.nash@venturidm.com",
    description="A small library for working with the Burp Suite API",
    url="https://github.com/Julian-Nash/burpsuite",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
        ],
)