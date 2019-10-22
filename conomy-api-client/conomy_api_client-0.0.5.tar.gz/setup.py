import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='conomy_api_client',
    version="0.0.5",
    author='Andrey Suglobov',
    author_email='suglobov@conomy.ru',
    description='Client for access to "Conomy" microservices',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.conomy.net/suglobov/conomy-api-client.git',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
