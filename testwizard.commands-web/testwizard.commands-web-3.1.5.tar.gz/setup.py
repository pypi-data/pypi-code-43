import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="testwizard.commands-web",
    version="3.1.5",
    author="Eurofins Digital Testing - Belgium",
    author_email="support-be@eurofins.com",
    description="Testwizard Web commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['testwizard.commands_web'],
    install_requires=[
        'testwizard.commands-core==3.1.5'
    ],
    classifiers=[
        "Programming Language :: Python :: 3.3",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
    ],
)




















