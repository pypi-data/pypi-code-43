import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="trivial_tools",
    version="2",
    author="Igor Zyktin",
    author_email="nicord@yandex.ru",
    description="Trivial tools for various scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IgorZyktin/trivial_tools",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
