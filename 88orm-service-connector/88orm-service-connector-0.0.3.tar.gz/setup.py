import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="88orm-service-connector",
    version="0.0.3",
    author="Rimba Prayoga",
    author_email="rimba47prayoga@gmail.com",
    description="ORM Service Connector",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://pypi.python.org/pypi/88orm-service-connector/",
    packages=["orm_service_connector88"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "Django >= 2.2.6",
        "requests"
    ]
)
