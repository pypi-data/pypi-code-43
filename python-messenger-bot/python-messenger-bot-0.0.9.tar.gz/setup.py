import setuptools

with open("README.md", "r") as fh:
    long_description=fh.read()

setuptools.setup(
    name="python-messenger-bot",
    version="0.0.9",
    author="Gello Mark Vito",
    author_email="gmcvito@gmail.com",
    description="Wrapper for Facebook Messenger Platform (bot).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gellowmellow/python-messenger-bot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)