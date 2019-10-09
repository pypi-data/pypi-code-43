import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="chat-app",
    version="1.1.6",
    author="Arin Khare",
    author_email="arinmkhare@gmail.com",
    description="Allows people to chat with others through terminal",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lol-cubes/chat-app",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=["cryptography"]
)
